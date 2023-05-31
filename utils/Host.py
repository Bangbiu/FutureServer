from utils.DataBase import *
from utils.Template import Template

import json

# from utils.Log import *


class Host(DataObject):
    owner_id: str
    name: str
    address: str
    contacts: str
    mobile: str
    industry: str
    env_desc: str
    products: str

    token: int
    registered: bool
    table: str = "host"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.ID == -1:
            self.__dict__["ID"] = Host.insert(**kwargs)

    def register(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)
        self.registered = True
        return True

    def add_token(self, num: int):
        self.token += int(num)
        return self.token

    def use_token(self):
        self.token -= 1
        return self.token


    def fetch_template(self):
        temp = Template(industry=self.industry)
        if temp.ID == -1:
            temp = Template(industry="default")
        content = json.loads(temp.content)
        return content

    def token_available(self):
        # Log.raise_error(EH.USER_TOKEN_RUN_OUT, self.ID)
        return self.token > 0

    @staticmethod
    def replace_choices(temp, key, choices):
        params = temp["paramsArr"]
        for param in params:
            if param["key"] == key:
                param["choices"] = choices
