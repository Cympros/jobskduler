# coding=utf-8
# 数据库操作类
import os
import sys
import sqlite3

root_path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(root_path)

from utils import utils_logger


class DataBaseOpenHelper():
    def __init__(self, db_path):
        self.db_path = db_path

    def exec_sql(self, sql):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = self.dict_factory
            cusor = conn.cursor()
            cusor.execute(sql)
            result = cusor.fetchall()
            conn.commit()
        except:
            utils_logger.log("DataBaseOpenHelper#exec_sql caught exception", sql)
        finally:
            if conn is not None:
                conn.close()
        return result

    @staticmethod
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
