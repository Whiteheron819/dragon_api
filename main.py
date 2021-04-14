import os
import datetime

import requests
from dotenv import load_dotenv

load_dotenv()
DATE_FORMAT = "%Y-%m-%d"
BEGIN_DATE = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime(DATE_FORMAT)
END_DATE = datetime.datetime.today().strftime(DATE_FORMAT)


URL = f'https://api.aqsi.ru/pub/v2/Receipts?filtered.BeginDate={BEGIN_DATE}&filtered.EndDate={END_DATE}&filtered.Operation=1'
TOKEN = os.getenv('TOKEN')


def get_orders():
    amount_rub = 0
    headers = {
        "x-client-key": TOKEN
    }
    orders = requests.get(URL, headers=headers).json()['rows']
    for i in range(len(orders)):
        if orders[i]['content']['checkClose']['payments'][0]['acquiringData'] is None:
            amount_rub += int(orders[i]['content']['checkClose']['payments'][0]['amount'])
    return amount_rub


def create_document(day_amount):
    if day_amount > 0:
        pass


if __name__ == '__main__':
    print(get_orders())
    print(BEGIN_DATE)
    print(END_DATE)
