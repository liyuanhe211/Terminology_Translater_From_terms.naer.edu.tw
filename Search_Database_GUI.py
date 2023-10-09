# -*- coding: utf-8 -*-

# TODO: 显示检索进度进度条
# TODO: 未检索到的处理
# TODO: 检查数据库解压功能

__author__ = 'LiYuanhe'

import os
import subprocess
from datetime import datetime

# import pathlib
# parent_path = str(pathlib.Path(__file__).parent.resolve())
# sys.path.insert(0,parent_path)

from Python_Lib.My_Lib_PyQt6 import *
import dataset
from sqlalchemy import create_engine, or_


Application = QtWidgets.QApplication(sys.argv)
font = Application.font()
font.setFamily("Arial")
Application.setFont(font)

if platform.system() == 'Windows':
    import ctypes

    APPID = 'LYH.XXXXXXXXXX.0.1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APPID)
    Application.setWindowIcon(QtGui.QIcon('UI/XXXXXXXXXX.png'))
    # matplotlib_DPI_setting = get_matplotlib_DPI_setting(Windows_DPI_ratio)

if __name__ == '__main__':
    pyqt_ui_compile('Main.py')
    from UI.Main import Ui_Form

def check_and_decompress_db():
    import zipfile
    if not os.path.exists("Database.db"):
        print("Decompressing Database (This will only be performed once for new download)...", end=" ",flush=True)
        with open('Database.zip', 'wb') as out_file:
            for i in os.listdir("."):
                if i.startswith("Database.zip.part"):
                    with open(i, 'rb') as chunk_file:
                        out_file.write(chunk_file.read())

        with zipfile.ZipFile("Database.zip", 'r') as zip_ref:
            zip_ref.extractall("./")

        os.remove("Database.zip")

        print("Done.")

class MyWidget(Ui_Form, QtWidgets.QWidget, Qt_Widget_Common_Functions):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.cached_result = {}
        self.current_buttons = OrderedDict()
        self.category_checkboxes = {}
        self.current_results = None

        connect_once(self.keyword_lineEdit.returnPressed, self.search_keywords)
        connect_once(self.select_none_pushButton, self.toggle_categories)

        self.keyword_lineEdit.setFocus()

        self.show()

        print("Connecting database...", end=" ", flush=True)
        self.status_label.setText("Connecting database... ")
        Application.processEvents()
        check_and_decompress_db()
        self.db = dataset.connect('sqlite:///Database.db')
        print("Done.")
        self.status_label.setText("Ready.")

        Application.processEvents()

        self.center_the_widget()

    def search_keywords(self):
        self.current_buttons.clear()
        for i in reversed(range(self.buttons_horizontalLayout.count())):
            self.buttons_horizontalLayout.itemAt(i).widget().setParent(None)

        keywords = self.keyword_lineEdit.text().split(',')

        for keyword in keywords:
            record_key = keyword
            keyword = keyword.strip()
            results = self.search_db(keyword)
            if not results and re.sub(r'(es|yl|ed)$', '', keyword)!=keyword:
                stripped_keyword = re.sub(r'(es|s|yl|ed)$', '', keyword)
                results = self.search_db(stripped_keyword,record_key=record_key)
            if not results and keyword.endswith("s"):
                stripped_keyword = keyword[:-1]
                results = self.search_db(stripped_keyword,record_key=record_key)
            if not results and ' ' in keyword:
                for word in keyword.split():
                    results = self.search_db(word)
                    if results:
                        self.add_button(word)
                    else:
                        results = self.search_db("".join(x for x in word if x.isalpha()))
            if results:
                self.add_button(keyword)

        if self.current_buttons:
            tuple(self.current_buttons.values())[0].click()
        else:
            self.update_table()

    def search_db(self, query: str, record_key: str = None) -> List[OrderedDict]:
        print("Searching for",query)
        self.status_label.setText("Searching for "+query+'...')
        Application.processEvents()
        table = self.db['data']
        if has_chinese_char(query):
            results = table.find(table.table.columns.Chinese.ilike(f'%{query}%'))
        else:
            results = table.find(table.table.columns.English.ilike(f'%{query}%'))
        ret = list(results)
        print("Matched",len(ret))
        self.status_label.setText("Matched "+str(len(ret))+' for '+query+".")
        Application.processEvents()

        # sort by relevance
        def sort_score(query:str,match:str,translate:str):
            query = query.lower()
            match = match.lower()
            contain_as_word = query in match.split()
            if translate is None:
                translate = ""
            return (not contain_as_word, len(match), match.find(query), match, translate)

        if has_chinese_char(query):
            ret.sort(key=lambda x:sort_score(query,x['Chinese'],x['English']))
        else:
            ret.sort(key=lambda x:sort_score(query,x['English'],x["Chinese"]))

        if record_key is None:
            record_key = query
        self.cached_result[record_key] = ret
        return ret

    def add_button(self, text: str):
        button = QPushButton(text)
        connect_once(button, lambda: self.update_table(self.cached_result[text]))
        self.buttons_horizontalLayout.addWidget(button)
        self.current_buttons[text] = button
        button = QPushButton(text)
        connect_once(button, lambda: self.update_table(self.cached_result[text]))
        history_layout = self.history_scrollArea.widget().layout()
        history_layout.insertWidget(history_layout.count()-1,button)

    def update_table(self, results=None, is_category_change=False):
        if results is None:
            results = []
            self.tableWidget.setRowCount(0)
            self.update_categories(results)
            return

        row_count = 0
        self.current_results = results

        for i, result in enumerate(results):
            # print(result)
            if not is_category_change or self.category_checkboxes[result['Category']].isChecked():
                # print("pass")
                row_count+=1
                self.tableWidget.setRowCount(row_count)
                self.tableWidget.setItem(row_count-1, 0, QTableWidgetItem(result['English']))
                self.tableWidget.setItem(row_count-1, 1, QTableWidgetItem(result['Chinese']))
                self.tableWidget.setItem(row_count-1, 2, QTableWidgetItem(result['Category']))

        if not is_category_change:
            self.update_categories(results)

        self.resize_table_column()

    def category_clicked(self):
        self.update_table(self.current_results,is_category_change=True)

    def update_categories(self, results):
        categories_layout = self.category_scrollArea.widget().layout()
        for i in reversed(range(categories_layout.count())):
            widget = categories_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        categories = OrderedDict()
        for result in results:
            category = result['Category']
            if category in categories:
                categories[category] += 1
            else:
                categories[category] = 1

        # for category, count in sorted(list(categories.items()),key=lambda x:x[1],reverse=True):
        for category, count in categories.items():
            checkbox = QCheckBox(f"{category} ({count})")
            self.category_scrollArea.widget().layout().addWidget(checkbox)
            checkbox.setChecked(True)
            connect_once(checkbox,self.category_clicked)
            self.category_checkboxes[category] = checkbox
        self.category_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.category_scrollArea.widget().layout().addItem(self.category_spacer)

    def toggle_categories(self):
        if self.category_scrollArea.widget().layout().count():
            select_all = self.select_none_pushButton.text() == 'Select All'
            self.select_none_pushButton.setText('Select All' if not select_all else 'Select None')

            for i in range(self.category_scrollArea.widget().layout().count()): # The last one is a spacer
                checkbox = self.category_scrollArea.widget().layout().itemAt(i).widget()
                if checkbox is not None and select_all and not checkbox.isChecked():
                    checkbox.click()
                if checkbox is not None and not select_all and checkbox.isChecked():
                    checkbox.click()

    def resize_table_column(self):
        total_width = self.tableWidget.width()-80
        max_widths = [0,0]
        # print(self.tableWidget.columnCount(),self.tableWidget.rowCount())
        # Calculate max widths
        for col in range(self.tableWidget.columnCount()-1):
            for row in range(self.tableWidget.rowCount()):
                # print(row,col)
                text = self.tableWidget.item(row, col).text()
                text_width = sum(2 if '\u4e00' <= ch <= '\u9fff' else 1 for ch in text)
                max_widths[col] = max(max_widths[col], text_width)


        # 保证category显示完全
        character_count = [self.tableWidget.item(row, 2).text() for row in range(self.tableWidget.rowCount())]
        character_count = max(len(x) for x in character_count)
        category_width = 15*character_count
        total_width-=category_width

        # Calculate proportional widths
        total_max_width = sum(max_widths)
        widths = [total_width * (w/total_max_width) for w in max_widths]
        widths+=[category_width]

        # Set column widths
        for i, width in enumerate(widths):
            self.tableWidget.setColumnWidth(i, int(width))

if __name__ == '__main__':
    gui = MyWidget()

    gui.show()
    sys.exit(Application.exec())
