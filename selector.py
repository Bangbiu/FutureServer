import sys

sys.path.append('')
from utils.DataBase import *


class SysArg:
    table: str = "user" if len(sys.argv) < 2 else sys.argv[1]
    cond: str = "ID>0" if len(sys.argv) < 3 else sys.argv[2].replace("}",">").replace("{","<")
    col: str = "*" if len(sys.argv) < 4 else sys.argv[3].replace("all", "*")
    clip: int = 10 if len(sys.argv) < 5 else int(sys.argv[4])

def reg_cell(cell, clip):
    res = ""
    cur_len = 0
    for char in cell:
        codes = ord(char)
        if codes <= 126:  # Half
            cur_len += 1
            res += char
        elif cur_len == clip - 1:
            cur_len += 1
            res += " "
        else:
            cur_len += 2
            res += char

        if cur_len >= clip:
            return res
    return res + "".join([" "] * (clip - cur_len))


def printRow(rec, clips):
    formater = "|".join(["{}"] * len(rec))
    print("|", end="")

    for index, cell in enumerate(rec):
        print(reg_cell(str(cell), clips[index]) + "|", end="")

    print()


if __name__ == "__main__":
    DataBase.initialize()
    DataBase.fetcher.execute("select {} from {} where {}".format(SysArg.col, SysArg.table, SysArg.cond))

    recs = DataBase.fetcher.fetchall()
    keys = list(map(lambda x: x[0], DataBase.fetcher.description))
    clips = [SysArg.clip] * len(keys)

    printRow(keys, clips)
    for row in recs:
        printRow(row, clips)

    DataBase.finalize()
