from utils.Client import Client
class Partner(Client):
    name: str
    identification: str
    address: str
    email: str
    district: int
    wxsp_appid: str = "wxa66e209d2eb26126"
    wxsp_secret: str = "fbc6804e5d3a93db3a8f39c730242013"
    table: str = "partner"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.ID == -1:
            self.__dict__["ID"] = Partner.insert(**kwargs)
