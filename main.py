import os
import datetime

import requests
from dotenv import load_dotenv

load_dotenv()
DATE_FORMAT = "%Y-%m-%d"
BEGIN_DATE = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime(DATE_FORMAT)
END_DATE = datetime.datetime.today().strftime(DATE_FORMAT)
NO_MONEY_MESSAGE = 'Нет продаж по наличным за день'


AQSI_URL = f'https://api.aqsi.ru/pub/v2/Receipts?filtered.BeginDate={BEGIN_DATE}&filtered.EndDate={END_DATE}&filtered.Operation=1'
AQSI_TOKEN = os.getenv('AQSI_TOKEN')
MOE_DELO_URL = 'url'
MOE_DELO_TOKEN = os.getenv('MOE_DELO_TOKEN')


def get_orders():
    amount_rub = 0
    headers = {
        "x-client-key": AQSI_TOKEN
    }
    orders = requests.get(AQSI_URL, headers=headers).json()['rows']
    for i in range(len(orders)):
        if orders[i]['content']['checkClose']['payments'][0]['acquiringData'] is None:
            amount_rub += int(orders[i]['content']['checkClose']['payments'][0]['amount'])
    return amount_rub


def create_document(day_amount):
    headers = {
        "key": MOE_DELO_TOKEN
    }
    if day_amount == 0:
        return NO_MONEY_MESSAGE
    else:
        return day_amount


if __name__ == '__main__':
    print(create_document(get_orders()))
