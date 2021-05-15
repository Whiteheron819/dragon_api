import os
import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

DATE_FORMAT = "%Y-%m-%d"
BEGIN_DATE = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime(DATE_FORMAT)
END_DATE = datetime.datetime.today().strftime(DATE_FORMAT)
ALREADY_HAVE_ERROR_MESSAGE = 'Такая смена уже существует!'
NO_MONEY_MESSAGE = 'Нет продаж по наличным за день'
SUCCESS_MESSAGE = 'Выгрузка успешна'
AQSI_URL = f'https://api.aqsi.ru/pub/v2/Receipts?filtered.BeginDate={BEGIN_DATE}&filtered.EndDate={END_DATE}&filtered.Operation=1'
AQSI_TOKEN = os.getenv('AQSI_TOKEN')
MOE_DELO_URL = 'https://restapi.moedelo.org/accounting/api/v1/cashier/1/retailRevenue'
MOE_DELO_DOCS_URL = f'https://restapi.moedelo.org/accounting/api/v1/cashier/1/retailRevenue?afterDate={END_DATE}'
MOE_DELO_TOKEN = os.getenv('MOE_DELO_TOKEN')
FIRM_INFO = os.getenv('FIRM_INFO')


def get_orders():
    amount_rub = 0
    headers = {
        "x-client-key": AQSI_TOKEN
    }
    orders = requests.get(AQSI_URL, headers=headers).json()['rows']
    z = requests.get(AQSI_URL, headers=headers).json()['rows'][0]['shiftNumber']
    for i in range(len(orders)):
        if orders[i]['content']['checkClose']['payments'][0]['acquiringData'] is None:
            amount_rub += int(orders[i]['content']['checkClose']['payments'][0]['amount'])
    return amount_rub, z


def create_document(day_amount, z_number):
    headers = {
        "md-api-key": MOE_DELO_TOKEN
    }
    day_count = requests.get(MOE_DELO_DOCS_URL, headers=headers).json()['ResourceList'][0]['ZReportNumber']
    if day_amount == 0:
        return NO_MONEY_MESSAGE
    elif day_count == z_number:
        return ALREADY_HAVE_ERROR_MESSAGE
    else:
        document = {
            "DocDate": BEGIN_DATE,
            "Description": f"Отчёт о продаже на точке {FIRM_INFO} на сумму {day_amount} руб",
            "Sum": day_amount,
            "ZReportNumber": z_number
        }
        requests.post(MOE_DELO_URL, data=document, headers=headers).json()
        return SUCCESS_MESSAGE


if __name__ == '__main__':
    print(create_document(get_orders()[0], get_orders()[1]))
