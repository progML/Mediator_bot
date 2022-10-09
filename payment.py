import json
from random import randint
import requests

from config import QIWI_TOKEN, QIWI_ACCOUNT
import pyqiwi

wallet = pyqiwi.Wallet(token=QIWI_TOKEN, number=QIWI_ACCOUNT)
comment = randint(10000, 99999)


def random_comment():
    return randint(10000, 99999)


def payment_history_last():
    s = requests.Session()
    s.headers['authorization'] = 'Bearer ' + QIWI_TOKEN
    parameters = {'rows': '20', 'operation': 'IN'}
    h = s.get('https://edge.qiwi.com/payment-history/v1/persons/' + QIWI_ACCOUNT + '/payments', params=parameters)
    req = json.loads(h.text)
    return req


def wallet_money(phone, amount):
    payment = "ds"
    return payment
