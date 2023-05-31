from utils.DataBase import *


class Template(DataObject):
    ID: int
    industry: str
    content: str
    table: str = "template"



    