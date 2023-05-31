from utils.DataBase import *


class Bill(DataObject):
    prepay_id: str
    orderno: str
    openid: str
    time: str
    pkgs: str
    cart: str
    token: int
    price: float
    status: int

    table: str = "bill"
