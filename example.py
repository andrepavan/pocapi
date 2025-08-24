from PoCAPI import PoCAPI

def main():
    
    book_model = {
        "name": "book",
        "url":  "books",
        "columns": [
            {"name": "id",      "type": "integer",  "pk": True},
            {"name": "title",   "type": "string",   "nullable": False},
            {"name": "author",  "type": "string",   "nullable": True},
        ]
    }

    person_model = {
        "name": "person",       # "url" defaults to "name" + "s" ("persons", "books", etc...)
        "columns": [
            {"name": "id"},     # when name = id, defaults are: type=integer and pk=True.
            {"name": "name"},   # "nullable" defaults to false.
            {"name": "email"},  # "type" defaults to string (except for "id")
        ]
    }
    
    
    # poc_api = PoCAPI(base_url='/app', port=5000, db_path='example.db')
    poc_api = PoCAPI()

    poc_api.add_model(book_model)
    poc_api.add_model(person_model)

    
    book_default_data = [
        {"title": "Nineteen Eighty-Four",   "author": "George Orwell"},
        {"title": "Fahrenheit 451",         "author": "Ray Bradbury"},
        {"title": "Brave New World",        "author": "Aldous Huxley"},
    ]
    
    person_default_data = [
        {"name": "Marty McFly",     "email": "marty@mcfly.moc"},
        {"name": "Ferris Bueller",  "email": "fbueller@fbdayoff.moc"},
        {"name": "André",           "email": "andre@mail.moc"},        
    ]
    
    poc_api.add_default_data("book", book_default_data)

    poc_api.add_default_data("person", person_default_data)


    poc_api.run()


main()

