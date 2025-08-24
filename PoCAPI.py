
from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, MetaData, String
from sqlalchemy import insert

TYPE_MAP = {
    "integer": Integer,
    "string": String
}

class PoCAPI:

    def __init__(self, base_url='/app', port=5000, db_path='pocapi.db'):
        
        self.base_url       = base_url
        self.port           = port
        self.app            = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI']          = f'sqlite:///{db_path}'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS']   = False
        self.db             = SQLAlchemy(self.app)
        self.models         = {}
        self.default_data   = {}
        CORS(self.app)

    def add_model(self, model):

        if not model.get('db_model'):
            
            model_name          = model.get('name').lower()
            db_model_attributes = {'__tablename__': model_name}

            if not model.get('path'):
                model['path'] = model_name + 's'

            for column in model.get('columns'):

                column_name = column.get('name').lower()

                if column_name == 'id' and (not column.get('type')) and (not column.get('pk')):
                    column['type']  = 'integer'
                    column['pk']    = True

                column_type     = TYPE_MAP[column.get('type', 'string')]
                column_pk       = column.get('pk')
                column_nullable = column.get('nullable')

                db_model_attributes[column_name] = Column(column_type, primary_key=column_pk, nullable=column_nullable)
            
            def to_dict(self):
                return {col.name: getattr(self, col.name) for col in self.__table__.columns}
            
            db_model_attributes['to_dict'] = to_dict

            db_model = type(model_name.capitalize(), (self.db.Model,), db_model_attributes)

            model['db_model'] = db_model


        self.models[model_name] = model

    def add_default_data(self, model_name, data):

        if not self.default_data.get(model_name):
            self.default_data[model_name] = []
        
        for item in data:
            self.default_data[model_name].append(item)


    def __generate_list(self, model):
        def _list():

            page    = int(request.args.get('page', 1))
            limit   = int(request.args.get('limit', 10))
            query   = model.get('db_model').query

            for column in model.get('columns'):

                match column.get('type'):
                    case 'integer':
                        filterStart = request.args.get(column.get('name')+'_start')
                        filterEnd   = request.args.get(column.get('name')+'_end')
                        filterValue = request.args.get(column.get('name'))

                        if filterStart:
                            query = query.filter(getattr(model.get('db_model'), column.get('name')) >= filterStart)

                        if filterEnd:
                            query = query.filter(getattr(model.get('db_model'), column.get('name')) <= filterEnd)
                        
                        if filterValue:
                            query = query.filter(getattr(model.get('db_model'), column.get('name')) == filterValue)
                        
                    case _:
                        filterOp    = request.args.get(column.get('name')+'_op')
                        filterValue = request.args.get(column.get('name')+'_value')

                        if (filterOp and filterValue):
                            match filterOp.upper():
                                case 'STARTSWITH':
                                    query = query.filter(getattr(model.get('db_model'), column.get('name')).ilike(f"{filterValue}%"))
                                case 'CONTAINS':
                                    query = query.filter(getattr(model.get('db_model'), column.get('name')).ilike(f"%{filterValue}%"))
                                case _:
                                    query = query.filter(getattr(model.get('db_model'), column.get('name')) == filterValue)


            data = query.offset((page - 1) * limit).limit(limit).all()
            data = [d.to_dict() for d in data]

            total       = query.count()
            response    = make_response(jsonify(data))
            response.headers["X-Total-Count"] = total
            response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"
            return response
        
        return _list


    def run(self):
        
        # Add API rules for each model.
        print('-------------------------------------')
        for model_name in self.models:
            model = self.models[model_name]

            print('ROUTE:', '[GET]', self.base_url + '/' + model['path'])
            self.app.add_url_rule(self.base_url + '/' + model['path'],
                                  model['path'],
                                  self.__generate_list(model),
                                  methods=["GET"])
        print('-------------------------------------')

        # Create db tables.
        with self.app.app_context():
            self.db.create_all()


            # Insert default data to each table (only if table is empty).
            for model_name in self.default_data:

                db_model = self.models[model_name]['db_model']

                if not db_model.query.first():
                
                    for data in self.default_data.get(model_name):

                        with self.db.engine.connect() as connection:
                            connection.execute(insert(db_model), data)
                            connection.commit()


        self.app.run(debug=False, port=self.port)


    