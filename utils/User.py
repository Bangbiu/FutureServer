#from __future__ import annotations

from utils.Host import Host
from utils.Client import Client


class User(Client):
    nickName: str
    realName: str
    host_id: int
    host: Host
    wxsp_appid: str = "wx8210ac9da791631f"
    wxsp_secret: str = "5ca6b92859a65137ec41be4ed3e924d2"
    table: str = "user"

    '''
    @classmethod
    def __new__(cls, **kwargs):
        return object.__new__(cls, **kwargs)
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.ID == -1:
            self.__dict__["ID"] = User.insert(**kwargs)
            self.__dict__["host"] = Host(owner_id=self.ID)
            self.host_id = self.host.ID
        else:
            self.__dict__["host"] = Host(ID=self.host_id)

    def fetch_template(self):
        return self.host.fetch_template()


pool = {}
