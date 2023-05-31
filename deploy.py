import os
import sys
import json
from typing import Union

import qrcode

sys.path.append('')

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from utils.DataBase import *
from utils.Log import *
from utils.RequestType import *
from utils.User import User
from utils.Partner import Partner
from utils.Template import Template

import utils.chatapi as chatapi
import utils.Bussiness as Bussiness

origins = ["*"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_headers=["*"],
)


@app.post("/command")
def command(args: CommandParam):
    model = "gpt-3.5-turbo"
    prompt = args.prompt
    usr = User(openid=args.openid)

    # Log Request
    Log(AH.USER_COMMAND, usr.ID, prompt)
    # Check Availability
    if not usr.host.token_available():
        Log.raise_error(EH.HOST_TOKEN_RUN_OUT, usr.ID)
    # Invoke API
    result = chatapi.request(prompt, model)
    # Log Result
    Log(AH.RESPONSE_COMMAND, usr.ID, result)
    # Take User Token
    usr.host.use_token()

    return result


@app.post("/chat")
def chat(args: ChatParam):
    usr = User(openid=args.openid)
    recentMsg = args.history[len(args.history) - 1]["content"]
    Log(AH.USER_CHAT, args.openid, recentMsg)

    if str(recentMsg).startswith("/"):
        return "Not Usable"

    # Check Token
    if len(args.history) <= 3 and not usr.host.token_available():
        Log.raise_error(EH.HOST_TOKEN_RUN_OUT, usr.ID)

    usr.host.use_token()

    # Check History Size
    hisize = 0
    for msg in args.history:
        hisize += len(str(msg["content"]).encode())

    if hisize > chatapi.max_token:
        Log.raiseError(EH.USER_EXCEED_MAX_TOKEN, args.openid)

    result = chatapi.chat(args.history)
    # result = "placeHolder"

    Log(AH.RESPONSE_CHAT, args.openid, result)

    return result


@app.post("/login_user")
def login_user(args: LoginParam):
    return User.login_code(args.code)


@app.post("/get_user_info")
def get_user_info(args: SessionParam):
    usr = User(openid=args.openid)
    user_info = usr.fetch()
    user_info["host"] = usr.host.fetch()
    return user_info


@app.post("/login_partner")
def login_partner(args: LoginParam):
    return Partner.login_code(args.code)


@app.post("/get_partner_info")
def get_user_info(args: SessionParam):
    return Partner(openid=args.openid).fetch()


@app.post("/get_template")
def get_template(args: TemplateParam):
    temp = Template(industry=args.industry)
    if temp.ID == -1:
        temp = Template(industry="default")
    print(json.loads(temp.content))
    return json.loads(temp.content)


@app.post("/get_packages")
def get_packages(args: RequestParam):
    if args.openid == "oPZOF5DvSQP3j8qAubLNyYTyKaB4":
        return Bussiness.packages
    return Bussiness.packages[:1]


@app.post("/reg_user")
def reg_user(args: UserRecord):
    print(args)
    return User(openid=args.openid).register(args.__dict__)


@app.post("/reg_host")
def reg_host(args: Union[HostRecord, HostUpdate]):
    openid = args.openid
    del args.openid
    return User(openid=openid).host.register(args.__dict__)


@app.post("/top_up")
def user_top_up(args: PayParam):
    return Bussiness.top_up_token(args)


@app.post("/notify")
def notify_payment(args: NotifyParam):
    Bussiness.payment_callback(args)


@app.get("/chat_log", response_class=HTMLResponse)
def chat_log():
    return Log.log_page()


@app.get("/partner_qr", response_class=FileResponse)
def partner_qr(ID: int):
    file = "qr/" + str(ID) + ".jpg"
    if os.path.exists(file):
        return file

    ptnr = Partner(ID=ID)
    if ptnr.ID == -1 or not ptnr.registered:
        return "qr/unregistered.jpg"

    name = ptnr.name
    data = "https://futuremind.mynatapp.cc" + "?invID=" + str(ID) + "&invName=" + name + "&invType=1"
    img = qrcode.make(data)
    img.save(file)
    return file


@app.on_event("startup")
def startup():
    DataBase.initialize()


@app.on_event("shutdown")
def shutdown():
    DataBase.finalize()


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=80)
