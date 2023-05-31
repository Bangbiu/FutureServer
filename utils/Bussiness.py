mchid = "1643072556"  # 商户号
pay_key = "thisapiisforrhythmfutureminiprog"  # 商户秘钥V3 使用V3接口必须使用V3秘钥
serial_num = "13B41D47E5CAE4A63E8A67BF5583CC1290146ED6"  # 证书序列号

packages = [
    {"token": 10, "price": 10.0},
    {"token": 1, "price": 0.01}
]

# ======================前三个参数在微信支付中可找到===============================
# ============ 商户号(mchid ) 在账户中心——商户信息——微信支付商户号 （是纯数字） ==================
# ============= 商户秘钥(pay_key) 在账户中心——API安全——APIv3秘钥 （需手动设置） ===================
# ============= 证书序列号(serial_num) 在账户中心——API安全——API证书 （需手动申请,通过后会有串证书序列号），申请完成后需要把证书下载到项目中，便于使用 ===================


appid = "wx8210ac9da791631f"  # 微信小程序appid
wx_secret = "5ca6b92859a65137ec41be4ed3e924d2"  # 微信小程序秘钥
# ============= 微信小程序appid 在产品中心——AppID账号管理——添加关联的AppID  ===================

WX_Pay_URL = "https://api.mch.weixin.qq.com/v3/pay/transactions/jsapi"
# ============= 微信支付调用地址,用于请求接收 预支付交易会话标识: prepay_id ===================


WX_Notify_URL = "https://futuremind.mynatapp.cc/"
# ============= 接收微信支付回调地址,必须是https ===================

import json
import decimal
import traceback
import string
import random as rnd
import base64

import requests

from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from sqlalchemy.util import b64encode
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from datetime import datetime

from utils.Log import *
from utils.Bill import Bill
from utils.User import User
from utils.RequestType import PayParam, NotifyParam


def orderno():
    """
    生成订单号
    :return:
    """
    # 下单时间的年月日毫秒12+随机数8位
    now_time = datetime.now()
    result = str(now_time.year) + str(now_time.month) + str(now_time.day) + str(now_time.microsecond) + str(
        rnd.randrange(10000000, 99999999))
    return result


def get_sign(sign_str):
    """
    定义生成签名的函数
    :param sign_str:
    :return:
    """
    try:
        with open(r'cert/apiclient_key.pem') as f:
            private_key = f.read()
        rsa_key = RSA.importKey(private_key)
        signer = pkcs1_15.new(rsa_key)
        digest = SHA256.new(sign_str.encode('utf-8'))
        # sign = b64encode(signer.sign(digest)).decode('utf-8')
        sign = b64encode(signer.sign(digest))
        return sign
    except Exception as e:
        Log.raise_error("Signing Error", 0, str(e))


def verify(check_data, signature, certificate):
    """
    验签函数
    :param check_data:
    :param signature:
    :param certificate:
    :return:
    """
    key = RSA.importKey(certificate)  # 这里直接用了解密后的证书，但没有去导出公钥，似乎也是可以的。怎么导公钥还没搞懂。
    verifier = pkcs1_15.new(key)
    hash_obj = SHA256.new(check_data.encode('utf8'))
    return verifier.verify(hash_obj, base64.b64decode(signature))


def decrypt(nonce, ciphertext, associated_data, pay_key):
    """
    AES解密
    :param nonce:
    :param ciphertext:
    :param associated_data:
    :param pay_key:
    :return:
    """
    key = pay_key
    key_bytes = str.encode(key)
    nonce_bytes = str.encode(nonce)
    ad_bytes = str.encode(associated_data)
    data = base64.b64decode(ciphertext)
    aesgcm = AESGCM(key_bytes)
    return aesgcm.decrypt(nonce_bytes, data, ad_bytes)


def check_wx_cert(response, mchid, pay_key, serial_no):
    """
    微信平台证书
    :param response: 请求微信支付平台所对应的的接口返回的响应值
    :param mchid: 商户号
    :param pay_key: 商户号秘钥
    :param serial_no: 证书序列号
    :return:
    """
    wechatpay_serial, wechatpay_timestamp, wechatpay_nonce, wechatpay_signature, certificate = None, None, None, None, None
    try:
        # 11.应答签名验证
        wechatpay_serial = response.headers['Wechatpay-Serial']  # 获取HTTP头部中包括回调报文的证书序列号
        wechatpay_signature = response.headers['Wechatpay-Signature']  # 获取HTTP头部中包括回调报文的签名
        wechatpay_timestamp = response.headers['Wechatpay-Timestamp']  # 获取HTTP头部中包括回调报文的时间戳
        wechatpay_nonce = response.headers['Wechatpay-Nonce']  # 获取HTTP头部中包括回调报文的随机串
        # 11.1.获取微信平台证书 （等于又把前面的跑一遍，实际上应是获得一次证书就存起来，不用每次都重新获取一次）
        url2 = "https://api.mch.weixin.qq.com/v3/certificates"
        # 11.2.生成证书请求随机串
        random_str2 = ''.join(rnd.choice(string.ascii_uppercase + string.digits) for _ in range(32))
        # 11.3.生成证书请求时间戳
        time_stamps2 = str(int(time.time()))
        # 11.4.生成请求证书的签名串
        data2 = ""
        sign_str2 = f"GET\n{'/v3/certificates'}\n{time_stamps2}\n{random_str2}\n{data2}\n"
        # 11.5.生成签名
        sign2 = get_sign(sign_str2)
        # 11.6.生成HTTP请求头
        headers2 = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": 'WECHATPAY2-SHA256-RSA2048 '
                             + f'mchid="{mchid}",nonce_str="{random_str2}",signature="{sign2}",timestamp="{time_stamps2}",serial_no="{serial_no}"'
        }
        # 11.7.发送请求获得证书
        response2 = requests.get(url2, headers=headers2)  # 只需要请求头
        cert = response2.json()

        # 11.8.证书解密
        nonce = cert["data"][0]['encrypt_certificate']['nonce']
        ciphertext = cert["data"][0]['encrypt_certificate']['ciphertext']
        associated_data = cert["data"][0]['encrypt_certificate']['associated_data']
        serial_no = cert["data"][0]['serial_no']
        certificate = decrypt(nonce, ciphertext, associated_data, pay_key)
    except Exception as e:
        Log.raise_error(EH.CERT_VERIFY_FAILED, 0, f"微信平台证书验证报错：{e}；{traceback.format_exc()}")
    return wechatpay_serial, wechatpay_timestamp, wechatpay_nonce, wechatpay_signature, certificate, serial_no


def make_headers_v3(mchid, serial_num, data='', method='GET'):
    """
    定义微信支付请求接口中请求头认证
    :param mchid: 商户ID
    :param serial_num: 证书序列号
    :param data: 请求体内容
    :param method: 请求方法
    :return: headers(请求头)
    """
    # 4.定义生成签名的函数 get_sign(sign_str)
    # 5.生成请求随机串
    random_str = ''.join(rnd.choice(string.ascii_uppercase + string.digits) for _ in range(32))
    # 6.生成请求时间戳
    time_stamps = str(int(time.time()))
    # 7.生成签名串
    sign_str = f"{method}\n{'/v3/pay/transactions/jsapi'}\n{time_stamps}\n{random_str}\n{data}\n"
    # 8.生成签名
    sign = get_sign(sign_str)
    # 9.生成HTTP请求头
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'WECHATPAY2-SHA256-RSA2048 '
                         + f'mchid="{mchid}",nonce_str="{random_str}",signature="{sign}",timestamp="{time_stamps}",serial_no="{serial_num}"'
    }
    return headers, random_str, time_stamps


def payment_callback(feedback: NotifyParam):
    data = feedback.__dict__
    nonce = data['resource']['nonce']
    ciphertext = data['resource']['ciphertext']
    associated_data = data['resource']['associated_data']

    try:
        payment = decrypt(nonce, ciphertext, associated_data, pay_key)
    except Exception as e:
        Log.raise_error(EH.USER_PAYMENT_FAILED, 0, str(e))

    if not payment:
        Log.raise_error(EH.USER_PAYMENT_FAILED, 0)

    payment = eval(payment.decode('utf-8'))
    # payment = {
    #     "mchid": "xxxx",
    #     "appid": "xxxx",
    #     "out_trade_no": "20231654836163523608",
    #     "transaction_id": "4200001646202301065425000524",
    #     "trade_type": "JSAPI",
    #     "trade_state": "SUCCESS",
    #     "trade_state_desc": "\xe6\x94\xaf\xe4\xbb\x98\xe6\x88\x90\xe5\x8a\x9f",
    #     "bank_type": "OTHERS",
    #     "attach": "",
    #     "success_time": "2023-01-06T15:12:49+08:00",
    #     "payer": {
    #         "openid": "xxxxx"
    #     },
    #     "amount": {
    #         "total": 1,
    #         "payer_total": 1,
    #         "currency": "CNY",
    #         "payer_currency": "CNY"
    #     }
    # }
    orderno = payment["out_trade_no"]
    openid = payment["payer"]["openid"]
    zf_status = payment["trade_state"] == "SUCCESS"

    if zf_status:
        Log(AH.USER_TOPUP_SUCESS, openid, args=payment)
        bill = Bill(orderno=orderno)
        if bill.ID == -1:
            Log.raise_error(EH.USER_PAYMENT_FAILED, openid, desc=orderno)
        bill.status = 1
        User(openid=bill.openid).host.add_token(bill.token)
    else:
        Bill(orderno=orderno).status = -1
        Log.raise_error(EH.USER_PAYMENT_FAILED, openid, desc=orderno)


def top_up_token(bill: PayParam):
    try:
        price = 0.0
        token = 0
        for index, amount in enumerate(bill.purchase):
            price += packages[index]["price"] * amount
            token += packages[index]["token"] * amount
        price = decimal.Decimal(price).quantize(decimal.Decimal("0.00"))  # 充值金额,保留两位小数
        info = {
            "price": float(price),
            "token": int(token),
            "openid": bill.openid,
            "time": time_stamp(),
            "pkgs": str(packages),
            "cart": str(bill.purchase),
            "remark": "套餐充值: {}元 {}积分".format(price, token),
            "status": 0,
            "orderno": orderno()
        }

        # 3.生成统一下单的报文body
        url = WX_Pay_URL
        body = {
            "appid": appid,
            "mchid": mchid,
            "description": info["remark"],
            "out_trade_no": info["orderno"],
            "notify_url": WX_Notify_URL + "/notify",  # 后端接收回调通知的接口
            "amount": {"total": int(price * 100), "currency": "CNY"},  # 正式上线price要*100，微信金额单位为分（必须整型）。
            "payer": {"openid": bill.openid},
        }
        data = json.dumps(body)

        headers, random_str, time_stamps = make_headers_v3(mchid, serial_num, data=data, method='POST')

        # 10.发送请求获得prepay_id
        try:
            response = requests.post(url, data=data, headers=headers)  # 获取预支付交易会话标识（prepay_id）
            # print("预支付交易会话标识", response.text)
            if response.status_code == 200:
                wechatpay_serial, wechatpay_timestamp, wechatpay_nonce, wechatpay_signature, certificate, serial_no = check_wx_cert(
                    response, mchid, pay_key, serial_num)
                # 11.9签名验证
                if wechatpay_serial == serial_no:  # 应答签名中的序列号同证书序列号应相同
                    # print('serial_no match')
                    try:
                        data3 = f"{wechatpay_timestamp}\n{wechatpay_nonce}\n{response.text}\n"
                        verify(data3, wechatpay_signature, certificate)
                        prepay_id = response.json()['prepay_id']
                        # print('The signature is valid.')
                        # 12.生成调起支付API需要的参数并返回前端
                        res = {
                            'orderno': info["orderno"],  # 订单号
                            'timeStamp': time_stamps,
                            'nonceStr': random_str,
                            'package': 'prepay_id=' + prepay_id,
                            'signType': "RSA",
                            'paySign': get_sign(
                                f"{appid}\n{time_stamps}\n{random_str}\n{'prepay_id=' + prepay_id}\n"),
                        }
                        Log(AH.USER_REQUEST_TOPUP, bill.openid, json.dumps(res), args=info)
                        info["prepay_id"] = prepay_id
                        Bill.insert(**info)
                        return res
                    except Exception as e:
                        Log.raise_error(EH.CERT_SERIAL_FAILED, bill.openid, str(e))
                else:
                    Log.raise_error(EH.CERT_COMPARE_FAILED, bill.openid,
                                    f"证书序列号比对失败【请求头中证书序列号：{wechatpay_serial}；本地存储证书序列号：{serial_no}；】")
            else:
                Log.raise_error(EH.PREPAY_API_ERROR, bill.openid,
                                f"获取预支付交易会话标识 接口报错【params：{data}；headers：{headers}；response：{response.text}】")
        except Exception as e:
            Log.raise_error(EH.WEPAY_TIME_OUT, bill.openid,
                            f"调用微信支付接口超时【params：{data}；headers：{headers}；】：{e},{traceback.format_exc()}")
    except Exception as e:
        Log.raise_error(EH.WEPAY_API_ERROR, bill.openid, f"微信支付接口报错：{e},{traceback.format_exc()}")
