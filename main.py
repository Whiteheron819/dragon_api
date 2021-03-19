import os

import requests
from dotenv import load_dotenv

load_dotenv()
BEGIN_DATE = '2021-03-11'
END_DATE = '2021-03-12'

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
            amount_rub += int(orders[i]['amount'])
    return amount_rub


if __name__ == '__main__':
    print(get_orders())
