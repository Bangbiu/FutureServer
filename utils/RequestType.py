from pydantic import BaseModel


class RequestParam(BaseModel):
    openid: str


class CommandParam(RequestParam):
    prompt: str


class ChatParam(RequestParam):
    history: list


class LoginParam(RequestParam):
    code: str


class SessionParam(RequestParam):
    session_key: str


class TemplateParam(RequestParam):
    industry: str


class UserRecord(RequestParam):
    nickName: str
    realName: str


class HostRecord(RequestParam):
    inviter_id: int
    owner_id: str
    name: str
    address: str
    contacts: str
    mobile: str
    industry: str
    env_desc: str
    products: str


class HostUpdate(RequestParam):
    env_desc: str
    products: str


class PayParam(RequestParam):
    purchase: list


class NotifyParam(BaseModel):
    id: str
    create_time: str
    resource_type: str
    event_type: str
    summary: str
    resource: object

    #     "resource": {
    #         "original_type":
    #         "transaction",
    #         "algorithm": "AEAD_AES_256_GCM",
    #         "ciphertext": "UF5gLXfe8qBv9qxQsf+/Mb6as+vbIhUS8Dm25qGIJIIdXTorUUjqZH1+"
    #                       "jMQxkxma/Gn9bOxeAoQWPEuIoJ2pB328Iv90jmHTrouoP3L60mjNgGJS8d3H8i1zAPBXCpP4mgvgRANWsw4pAWj1lFM5BZr4aP+"
    #                       "pNMc5TdwreGBG3rO9sbCLXsSRfW8pVZ7IfPnhPDTOWP3P1k5ikHedcRt4/HP69oDBEe5RSsD93wO/"
    #                       "lrIwycStVHyecBaliwpVMRnNnRCXqhlalNJ3NJ6jcgy32fP1J+L90ntwGyqMmZUS71P5TN1H0iH5rXNpRY9IF3pvN+"
    #                       "lei5IS86wEoVXkmEsPcJrHaabn7rghxuZoqwuauMIiMwBLllnEmgXfAbJA4FJy+"
    #                       "OLhZPrMWMkkiNCLcL069QlvhLXYi/0V9PQVTnvtA5RLarj26s4WSqTZ2I5VGHbTqSIZvZYK3F275KEbQsemYETl18xwZ+"
    #                       "WAuSrYaSKN/pKykK37vUGtT3FeIoJup2c6M8Ghull3OcVmqCOsgvU7/pNjl1rLKEJB6t/X9avcHv+feikwQBtBmd/b2qCeSrEpM7US",
    #         "associated_data": "transaction",
    #         "nonce": "cKEdw8eV9Bh0"
