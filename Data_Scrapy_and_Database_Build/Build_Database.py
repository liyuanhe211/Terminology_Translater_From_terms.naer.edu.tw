import dataset
from sqlalchemy import create_engine, or_
from os import listdir
from os.path import isfile, join
from Python_Lib.My_Lib_Office import read_xlsx

# Get all the excel files
mypath = 'Database' # Directory where the excel files are
files = [join(mypath, f) for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith('.xlsx')]

# Create a sqlite database
db = dataset.connect('sqlite:///Database.db')

# # Read all the xlsx files and insert into the database
# for file in files:
#     if os.path.isfile(file):
#         print(file)
#         data = read_xlsx(file)
#         table = db['data']
#         for row in data:
#             table.insert(dict(English=row[0],
#                               EnglishLink=row[1],
#                               Chinese=row[2],
#                               ChineseLink=row[3],
#                               Category=row[4]))


# self.db = dataset.connect('sqlite:///Database.db')
table = db['data']
print("Start Indexing...")
# Create index for English and Chinese columns
table.create_index(['English', 'Chinese'])
print("Finished.")