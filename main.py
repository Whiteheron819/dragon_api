import datetime
import logging
import os
import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import sleep
from dotenv import load_dotenv

load_dotenv()

DATE_FORMAT = "%Y-%m-%d"
BEGIN_DATE = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime(DATE_FORMAT)
END_DATE = datetime.datetime.today().strftime(DATE_FORMAT)
MAIL_FROM = os.getenv('MAIL_FROM')
MAIL_TO = os.getenv('MAIL_TO')
DESCRIPTION_MESSAGE = 'Отчёт о продаже на точке Студия старинного танца Хрустальный дракон (ИНН=7804535190) на сумму {day_amount} руб'
JSON_ERROR_MESSAGE = 'Ошибка чтения JSON: {error}'
ALREADY_HAVE_ERROR_MESSAGE = 'Такая смена уже существует!'
NO_MONEY_MESSAGE = 'Нет продаж по наличным за день'
SUCCESS_MESSAGE = 'Создан документ на сумму {day_amount} рублей, смена номер {z_number}'
EMAIL_SUBJECT = f'Отчёт о продажах за {END_DATE}'
AQSI_URL = f'https://api.aqsi.ru/pub/v2/Receipts?filtered.BeginDate={BEGIN_DATE}&filtered.EndDate={END_DATE}&filtered.Operation=1'
AQSI_TOKEN = os.getenv('AQSI_TOKEN')
MOE_DELO_URL = 'https://restapi.moedelo.org/accounting/api/v1/cashier/1/retailRevenue'
MOE_DELO_DOCS_URL = f'https://restapi.moedelo.org/accounting/api/v1/cashier/1/retailRevenue?afterDate={END_DATE}'
MOE_DELO_TOKEN = os.getenv('MOE_DELO_TOKEN')


def requests_get(url, headers):
    for i in range(10):
        r = requests.get(url=url, headers=headers)
        if r.status_code == 200:
            return r
        sleep(10)
    logging.critical(f'Failed to retrieve URL: {url}; status code: {r.status_code}')
    exit(1)


def requests_post(url, data, headers):
    for i in range(10):
        r = requests.post(url=url, data=data, headers=headers)
        if r.status_code == 200:
            return True
    logging.critical(f'Failed to post data to {url}; status code: {r.status_code}')
    exit(1)


def get_orders():
    amount_rub = 0
    headers = {
        "x-client-key": AQSI_TOKEN
    }
    rj = requests_get(url=AQSI_URL, headers=headers).json()
    if 'rows' in rj:
        orders = rj['rows']
        if isinstance(orders, list) and len(orders) > 0 and 'shiftNumber' in orders[0]:
            shift_number = orders[0]['shiftNumber']
            for i in range(len(orders)):
                if orders[i]['content']['checkClose']['payments'][0]['acquiringData'] is None:
                    amount_rub += int(orders[i]['content']['checkClose']['payments'][0]['amount'])
            return amount_rub, shift_number
    return 0, 0


def create_document(day_amount, z_number):
    if day_amount == 0:
        return NO_MONEY_MESSAGE
    headers = {
        "md-api-key": MOE_DELO_TOKEN
    }
    orders = requests_get(url=MOE_DELO_DOCS_URL, headers=headers).json()
    if orders['TotalCount'] != 0 and orders['ResourceList'][0]['ZReportNumber'] == z_number:
        return ALREADY_HAVE_ERROR_MESSAGE
    else:
        document = {
            "DocDate": BEGIN_DATE,
            "Description": DESCRIPTION_MESSAGE.format(day_amount=day_amount),
            "Sum": day_amount,
            "ZReportNumber": z_number
        }
        success = SUCCESS_MESSAGE.format(day_amount=day_amount, z_number=z_number)
        requests_post(url=MOE_DELO_URL, data=document, headers=headers)
        send_mail(success)
        return success


def send_mail(message):
    msg = MIMEMultipart()
    password = os.getenv('PASSWORD')
    msg['From'] = MAIL_FROM
    msg['To'] = MAIL_TO
    msg['Subject'] = EMAIL_SUBJECT
    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP('localhost', 25)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()


def main():
    try:
        rub, z_number = get_orders()
        logging.info(create_document(rub, z_number))
    except Exception as error:
        logging.info(JSON_ERROR_MESSAGE.format(error=error)), exit(1)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s; %(levelname)s; %(message)s',
        filename=__file__+'.txt'
    )
    main()
