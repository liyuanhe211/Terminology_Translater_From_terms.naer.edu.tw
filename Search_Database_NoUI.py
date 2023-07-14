import pandas as pd
import dataset
from sqlalchemy import create_engine, or_
from os import listdir
from os.path import isfile, join

from Search_Database_GUI import check_and_decompress_db

check_and_decompress_db()

# Get all the excel files
mypath = './' # Directory where the excel files are
files = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith('.xlsx')]

# Create a sqlite database
db = dataset.connect('sqlite:///Database.db')

# Function to search the database
def search_db(query, category=None):
    table = db['data']
    if category:
        results = table.find(or_(table.table.columns.English.like(f'%{query}%'), table.table.columns.Chinese.like(f'%{query}%')), Category=category)
    else:
        results = table.find(or_(table.table.columns.English.like(f'%{query}%'), table.table.columns.Chinese.like(f'%{query}%')))
    return results

# Example usage
for result in search_db('内聚力'):
    print(result)