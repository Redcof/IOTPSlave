import sqlite3

from IntsUtil.util import print_red

_author_ = "int_soumen"
_date_ = "2019-Jan-13"


class Database:
    """ init database """

    def __init__(self, db_file):
        self.__db = None
        self.__database = db_file
        self.__cursor = None
        self.__result = None
        pass

    """ connect to database """

    def connect(self):
        if self.__db is None:
            self.__db = sqlite3.connect(self.__database)
        self.__cursor = self.__db.cursor()
        pass

    """ disconnect from database """

    def disconnect(self):
        if self.__db is not None:
            self.__db.close()
            self.__db = None

    def commit(self):
        self.__db.commit()
        pass

    def rollback(self):
        self.__db.rollback()
        pass

    def query(self, query, params):
        self.__result = None
        try:
            self.__result = self.__cursor.execute(query, params)
        except Exception, e:
            print_red(e)
            pass
        return self.__result
        pass

