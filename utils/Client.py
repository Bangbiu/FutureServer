from utils.Log import *

import json
import requests


class Client(DataObject):
    openid: str
    last_login: str
    registered: bool
    wxsp_appid: str
    wxsp_secret: str

    def login(self):
        self.last_login = time_stamp()
        return self

    def register(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)
        self.registered = True
        return True

    @classmethod
    def login_code(cls, code: str) -> dict:
        url = 'https://api.weixin.qq.com/sns/jscode2session'
        grant_type = "authorization_code"

        # Make POST request
        response = requests.post(url, data={
            'appid': cls.wxsp_appid,
            'secret': cls.wxsp_secret,
            'js_code': code,
            'grant_type': grant_type,
        })

        if response.status_code == 200:
            info = json.loads(response.text)
            print(response.text)
            openid = info["openid"]
            # s_key = info["session_key"]
            cls(openid=openid).login()
            return info
        else:
            Log.raise_error(EH.USER_LOGIN_FAILED, code, response.text)