import os

def open_file(file):
    path = os.path.join(
        os.getcwd(),        
        'common/', 'db/', 'sql/', file
    )
    with open(path, "r") as file:
        return file.read()