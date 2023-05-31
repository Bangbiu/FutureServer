import datetime
import sqlite3


class DataBase:
    conn: sqlite3.Connection
    fetcher: sqlite3.Cursor

    @classmethod
    def __del__(cls):
        DataBase.finalize()

    @staticmethod
    def initialize():
        DataBase.conn = sqlite3.connect("data.db", check_same_thread=False)
        DataBase.fetcher = DataBase.conn.cursor()

    @staticmethod
    def execute(command: str, *args):
        cursor = DataBase.conn.cursor()
        rowid = cursor.execute(command, args).lastrowid
        cursor.close()
        DataBase.conn.commit()
        return rowid

    @staticmethod
    def fetch_host_templates(hostid, func):
        DataBase.fetcher.execute("select * from template where hostid = ? and func = ?", (hostid, func))
        return DataBase.fetcher.fetchall()

    @staticmethod
    def finalize():
        DataBase.fetcher.close()
        DataBase.conn.close()

    @staticmethod
    def attr_seg(**kwargs):
        return "(" + ", ".join(list(kwargs.keys())) + ") values(" + ", ".join(["?"] * len(kwargs)) + ")"

    @staticmethod
    def cond_seg(**kwargs):
        cond_list = []
        for key in kwargs.keys():
            cond_list.append(key + " = ?")
        return " and ".join(cond_list)


class DataObject:
    cursor: sqlite3.Cursor
    table: str = "None"
    ID: int

    def __init__(self, **kwargs):
        self.__dict__["cursor"] = DataBase.conn.cursor()
        cmd = "select * from {} where ".format(self.table) + DataBase.cond_seg(**kwargs)
        # print(self.table)
        # print(DataBase.cond_seg(**kwargs))
        # print(kwargs.values())
        self.cursor.execute(cmd, tuple(kwargs.values()))
        rec = self.cursor.fetchone()
        self.__dict__["ID"] = -1 if rec is None else rec[0]

    def __getattr__(self, name):
        self.cursor.execute("select {} from {} where ID = ?"
                            .format(name, self.table), (self.ID,))
        res = self.cursor.fetchone()
        return None if res is None else res[0]

    def __setattr__(self, key, value):
        if key in self.__dict__.keys(): return
        self.cursor.execute("update {} set {} = ? where ID = ?".format(self.table, key),
                            (value, self.ID))
        DataBase.conn.commit()

    def __del__(self):
        self.finalize()

    def fetch(self):
        self.cursor.execute("select * from {} where ID = ?".format(self.table), (self.ID,))
        data = self.cursor.fetchone()
        mapping = {}
        for index, key in enumerate(map(lambda x: x[0], self.cursor.description)):
            mapping[key] = data[index]
        return mapping

    def finalize(self):
        self.cursor.close()

    @classmethod
    def insert(cls, **kwargs):
        rowid = DataBase.execute(
            "insert into {} ".format(cls.table) + DataBase.attr_seg(**kwargs),
            *kwargs.values()
        )
        # DataBase.fetcher.execute("select ID from {} where rowid = ?".format(cls.table), (rowid,))
        # id = DataBase.fetcher.fetchone()[0]
        return rowid

    @classmethod
    def fetch_all(cls, condition: str = "ID > 0"):
        DataBase.fetcher.execute("select * from {} where ".format(cls.table) + condition)
        return DataBase.fetcher.fetchall()
