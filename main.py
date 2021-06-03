import datetime
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from dotenv import load_dotenv

load_dotenv()

DATE_FORMAT = "%Y-%m-%d"
BEGIN_DATE = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime(DATE_FORMAT)
END_DATE = datetime.datetime.today().strftime(DATE_FORMAT)
JSON_ERROR_MESSAGE = 'Ошибка чтения JSON: {error}'
ALREADY_HAVE_ERROR_MESSAGE = 'Такая смена уже существует!'
NO_MONEY_MESSAGE = 'Нет продаж по наличным за день'
SUCCESS_MESSAGE = 'Выгрузка успешна'
EMAIL_SUBJECT = f'Отчёт о продажах за {END_DATE}'
AQSI_URL = f'https://api.aqsi.ru/pub/v2/Receipts?filtered.BeginDate={BEGIN_DATE}&filtered.EndDate={END_DATE}&filtered.Operation=1'
AQSI_TOKEN = os.getenv('AQSI_TOKEN')
MOE_DELO_URL = 'https://restapi.moedelo.org/accounting/api/v1/cashier/1/retailRevenue'
MOE_DELO_DOCS_URL = f'https://restapi.moedelo.org/accounting/api/v1/cashier/1/retailRevenue?afterDate={END_DATE}'
MOE_DELO_TOKEN = os.getenv('MOE_DELO_TOKEN')


def get_orders():
    amount_rub = 0
    headers = {
        "x-client-key": AQSI_TOKEN
    }
    orders = requests.get(AQSI_URL, headers=headers).json()['rows']
    shift_number = orders[0]['shiftNumber']
    for i in range(len(orders)):
        if orders[i]['content']['checkClose']['payments'][0]['acquiringData'] is None:
            amount_rub += int(orders[i]['content']['checkClose']['payments'][0]['amount'])
    return amount_rub, shift_number


def create_document(day_amount, z_number):
    if day_amount == 0:
        return NO_MONEY_MESSAGE
    headers = {
        "md-api-key": MOE_DELO_TOKEN
    }
    orders = requests.get(MOE_DELO_DOCS_URL, headers=headers).json()
    if orders['TotalCount'] != 0 and orders['ResourceList'][0]['ZReportNumber'] == z_number:
        return ALREADY_HAVE_ERROR_MESSAGE
    else:
        document = {
            "DocDate": BEGIN_DATE,
            "Description": f"Отчёт о продаже на точке Студия старинного танца Хрустальный дракон (ИНН=7804535190) на сумму {day_amount} руб",
            "Sum": day_amount,
            "ZReportNumber": z_number
        }
        requests.post(MOE_DELO_URL, data=document, headers=headers).json()
        return f"Создан документ на сумму {day_amount}, номер смены {z_number}"


def send_mail(message):
    msg = MIMEMultipart()
    password = os.getenv('PASSWORD')
    msg['From'] = "Whiteheron819@gmail.com"
    msg['To'] = "nareiel@gmail.com"
    msg['Subject'] = EMAIL_SUBJECT

    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(msg['From'], password)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()


def main():
    try:
        rub, z_number = get_orders()
        logging.info(create_document(rub, z_number))
        if rub != 0:
            send_mail(f'Создан документ на сумму {rub} рублей, смена номер {z_number}')
    except Exception as error:
        logging.info(JSON_ERROR_MESSAGE.format(error=error))


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s; %(levelname)s; %(message)s',
        filename=__file__+'.txt'
    )
    main()
