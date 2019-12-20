from ExactGlobe import ExactApi
from configparser import ConfigParser

# create config parser and read 'config.ini'
cfg = ConfigParser()
cfg.read('config.ini')

# init the Exact API Class
ExactApi = ExactApi(cfg.get('EXACT', 'servername'), cfg.get('EXACT', 'database_name'), cfg.get('EXACT', 'database_server_name'),
                    cfg.get('EXACT', 'username'), cfg.get('EXACT', 'password'))


# Get the customer details from Exact
status, customer_details = ExactApi.getCustomerDetailsByID(204393)


# Create a new customer
xml_param = {
    'DebtorCode': '20191001',
    'DebtorNumber': '20191001',
    'AccountName': 'Kees Test Account Inc.',
    'Title': 'DHR',
    'Initials': 'J.',
    'FirstName': 'Joël',
    'LastName': 'van Amerongen',
    'MobileNumber': '08812345678',
    'PhoneNumber': '0882445433',
    'Address': 'Street 123',
    'City': 'New York',
    'Zip': '90210',
    'Email': 'support@customer.nl',
    'Country': 'NL',
    'WebAddress': 'https://google.nl/',
    'TransactionKey': ''
}

status, new_customer_data = ExactApi.addNewCustomer(xml_param)
