# -*- coding: utf-8 -*-
__author__ = 'LiYuanhe'

# import sys
# import pathlib
# parent_path = str(pathlib.Path(__file__).parent.resolve())
# sys.path.insert(0,parent_path)

from Python_Lib.My_Lib_Stock import *

def split_file(file_path, part_size):
    file_size = os.path.getsize(file_path)
    part_number = 0

    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(part_size)
            if not chunk:
                break

            part_number += 1
            part_name = f"{file_path}.part{part_number}"

            with open(part_name, 'wb') as part_file:
                part_file.write(chunk)

    return part_number

# Split file into parts of 100 MB
split_file('E:\My_Program\樂詞網专业术语中英翻译检索器\Database.zip', 80*1024*1024)
