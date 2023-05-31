import time
from fastapi import HTTPException
from utils.DataBase import DataObject

header = """
    <!DOCTYPE html>
    <html>

    <head>
        <meta charset="UTF-8">
        <title>Chat Log</title>
    </head>

    <body>
        <h1>fast</br>api</h1>
    </body>
"""


class strEnum:
    @classmethod
    def includes(self, item):
        return item in self.__dict__.values()


class ActionHeader(strEnum):
    USER_REQUEST_LOGIN = "User Request to Login"
    USER_REQUEST_INFO = "Request UserInfo"
    USER_REQUEST_DATA = "Request Data"
    USER_COMMAND = "User Command"
    USER_CHAT = "User Raise Chat"
    USER_REQUEST_TOPUP = "User Request Top up"
    USER_TOPUP_SUCESS = "User Top up Success"

    RESPONSE_COMMAND = "Response Command"
    RESPONSE_CHAT = "Response User Chat"


class ErrorHeader(strEnum):
    USER_LOGIN_FAILED = "User Login Failed"
    USER_REQ_FAILED = "Request Failed"
    USER_EXCEED_MAX_TOKEN = "Max Token Exceeeded"
    HOST_TOKEN_RUN_OUT = "User Token Used Up"

    CERT_SERIAL_FAILED = "Certificate Verification Failed"
    SIGN_ERROR = "Signing Error"
    CERT_COMPARE_FAILED = "Certificate Comparison Failed"
    CERT_VERIFY_FAILED = "Certificate Verification Failed"
    PREPAY_API_ERROR = "Prepay API Error"
    WEPAY_TIME_OUT = "WeChat Pay API Timeout"
    WEPAY_API_ERROR = "WeChat Pay API Error"
    USER_PAYMENT_FAILED = "WeChat Payment Failed"

class InfoHeader(ActionHeader, ErrorHeader):
    pass


AH = ActionHeader
EH = ErrorHeader
IH = InfoHeader

LogDesc = {

    AH.USER_REQUEST_LOGIN: "用户请求登录",
    AH.USER_CHAT: "用户请求聊天回复",
    AH.USER_COMMAND: "用户命令生成",
    AH.USER_REQUEST_INFO: "用户请求用户数据",
    AH.USER_REQUEST_DATA: "用户请求自定义数据",
    AH.RESPONSE_COMMAND: "回复生成命令",
    AH.RESPONSE_CHAT: "聊天回复",
    AH.USER_REQUEST_TOPUP: "用户请求充值",
    AH.USER_TOPUP_SUCESS: "用户充值成功",

    EH.USER_LOGIN_FAILED: "登录失败",
    EH.USER_REQ_FAILED: "用户请求失败",
    EH.HOST_TOKEN_RUN_OUT: "会话次数已用尽",
    EH.USER_EXCEED_MAX_TOKEN: "超过会话最大字数",

    EH.CERT_SERIAL_FAILED: "证书序列号验签失败",
    EH.SIGN_ERROR: "生成签名的函数方法报错",
    EH.CERT_COMPARE_FAILED: "证书序列号比对失败",
    EH.WEPAY_TIME_OUT: "调用微信支付接口超时",
    EH.WEPAY_API_ERROR: "微信支付接口报错",
    EH.CERT_VERIFY_FAILED: "微信平台证书验证报错",
    EH.USER_PAYMENT_FAILED: "用户支付失败"
}

codes = {

    AH.USER_REQUEST_LOGIN: 200,
    AH.USER_CHAT: 200,
    AH.USER_COMMAND: 200,
    AH.USER_REQUEST_INFO: 200,
    AH.USER_REQUEST_DATA: 200,
    AH.RESPONSE_COMMAND: 200,
    AH.RESPONSE_CHAT: 200,
    AH.USER_REQUEST_TOPUP: 200,
    AH.USER_TOPUP_SUCESS: 200,

    EH.USER_LOGIN_FAILED: 400,
    EH.USER_REQ_FAILED: 403,
    EH.HOST_TOKEN_RUN_OUT: 403,
    EH.USER_EXCEED_MAX_TOKEN: 403,

    EH.CERT_SERIAL_FAILED: 500,
    EH.SIGN_ERROR: 500,
    EH.CERT_COMPARE_FAILED: 500,
    EH.PREPAY_API_ERROR: 500,
    EH.WEPAY_TIME_OUT: 500,
    EH.WEPAY_API_ERROR: 500,
    EH.CERT_VERIFY_FAILED: 500,
    EH.USER_PAYMENT_FAILED: 400
}

AHShell = ["<-- ", " -->"]
EHShell = ["<!-- ", " --!>"]

HTML_Replace = {
    AHShell[0]: "<h3 style=\"color:blue\"><-- ",
    AHShell[1]: " --></h3>",
    EHShell[0]: "<h3 style=\"color:red\"><--! ",
    EHShell[1]: " --></h3>",
    "\n": "</br>"
}


def time_stamp():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


class Log(DataObject):
    table: str = "log"

    def __new__(cls, header: InfoHeader, user_id: int, msg: str = None, args: object = None):
        Log.insert(
            user_id=user_id, header=header,
            code=codes[header], time=time_stamp(),
            message=msg, args=str(args)
        )
        
    @staticmethod
    def raise_error(errType: ErrorHeader, userid: int, desc: str = None):
        Log(errType, userid, desc)
        if desc is None: desc = LogDesc[errType]
        raise HTTPException(status_code=codes[errType], detail=desc)

    @staticmethod
    def log_page():
        page = open(Log.logFile, 'r', encoding="utf-8").read()
        for key, value in HTML_Replace.items():
            page = page.replace(key, value)
        return page
