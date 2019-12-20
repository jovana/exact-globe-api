import requests
import json
from requests_ntlm import HttpNtlmAuth
import os
import unidecode
import xmltodict


class ExactApi(object):
    def __init__(self, p_ServerName, p_DatabaseName, p_DatabaseServerName, p_UserName, p_Password):
        self._serverName = p_ServerName                     # Ex 127.0.0.1:1234
        self._databaseName = p_DatabaseName                 # SQL Database name
        self._databaseServerName = p_DatabaseServerName     # Server name where the SQL engine is running on
        self._userName = p_UserName
        self._password = p_Password
        self._accountCodeLength = 20
        self._auth = HttpNtlmAuth(self._userName, self._password)

    def getFromToExact(self, endpoint, payload=None, update=False):
        """Post data to Exact

        Arguments:
            endpoint {[type]} -- [description]

        Keyword Arguments:
            payload {[type]} -- [description] (default: {None})
            update {bool} -- [description] (default: {False})

        Returns:
            [type] -- [description]
        """

        header = {
            'Accept': 'application/atom+xml',
            'Content-Type': 'application/atom+xml',
            'ServerName': self._databaseServerName,
            'DatabaseName': self._databaseName
        }

        uri = self._serverName + endpoint
        return requests.get(uri, headers=header, auth=self._auth, verify=False)

    def sendToExact(self, endpoint, payload=None, update=False):

        header = {
            'Accept': 'application/atom+xml',
            'Content-Type': 'application/atom+xml',
            'ServerName': self._databaseServerName,
            'DatabaseName': self._databaseName
        }

        uri = self._serverName + endpoint
        return requests.post(uri, payload, headers=header, auth=self._auth, verify=False)

    def addNewCustomer(self, p_CustomerParameters={}):
        """ Adding a new debtor to Exact

        Keyword Arguments:
            p_CustomerParameters {dict} -- [description] (default: {{}})

        Returns:
            [type] -- [description]
        """
        xml = self.__LoadXMLTemplate('ExactAddingDebtor').format(
            DebtorCode=p_CustomerParameters['DebtorCode'],
            AccountName=p_CustomerParameters['AccountName'],
            Title=p_CustomerParameters['Title'],
            Initials=p_CustomerParameters['Initials'],
            LastName=unidecode.unidecode(p_CustomerParameters['LastName']),
            FirstName=unidecode.unidecode(p_CustomerParameters['FirstName']),
            MobileNumber=p_CustomerParameters['MobileNumber'],
            PhoneNumber=p_CustomerParameters['PhoneNumber'],
            Address=p_CustomerParameters['Address'],
            City=p_CustomerParameters['City'],
            Zip=p_CustomerParameters['Zip'],
            Email=p_CustomerParameters['Email'],
            Country=p_CustomerParameters['Country'],
            WebAddress=p_CustomerParameters['WebAddress']
        )

        result = self.sendToExact("/Services/Exact.Entity.Rest.EG/Account", xml)
        if result == None:
            return False, None
        else:
            json_response = json.dumps(xmltodict.parse(result.content))
            if result.status_code == 200 or result.status_code == 201:
                return True, json.loads(json_response)
            else:
                return False, json.loads(json_response)

    def addNewInvoiceLine(self, p_InvoiceParameters):
        """ Adding a new invoice line to a debtor in Exact

        Keyword Arguments:
            p_CustomerParameters {dict} -- [description] (default: {{}})

        Returns:
            [type] -- [description]
        """

        transaction_key_placeholder = '<d:TransactionKey></d:TransactionKey>'
        if 'TransactionKey' in p_InvoiceParameters and not p_InvoiceParameters['TransactionKey'] == None:
            transaction_key_placeholder = '<d:TransactionKey>{0}</d:TransactionKey>'.format(p_InvoiceParameters['TransactionKey'])
        else:
            transaction_key_placeholder = ''

        xml = self.__LoadXMLTemplate('ExactAddingInvoiceLine').format(
            Description=p_InvoiceParameters['Description'],
            EntryDate=p_InvoiceParameters['EntryDate'],
            GLAccount=p_InvoiceParameters['GLAccount'],
            Amount=p_InvoiceParameters['Amount'],
            TransactionKey=transaction_key_placeholder
        )

        result = self.sendToExact("/Services/Exact.Entity.Rest.EG/FinancialLine", xml)
        if result == None:
            return False, None
        else:
            json_response = json.dumps(xmltodict.parse(result.content))
            if result.status_code == 200 or result.status_code == 201:
                return True, json.loads(json_response)
            else:
                return False, json.loads(json_response)

    def addNewCustomerInvoice(self, p_InvoiceParameters={}):
        """ Adding a new invoice to a debtor in Exact

        Keyword Arguments:
            p_CustomerParameters {dict} -- [description] (default: {{}})

        Returns:
            [type] -- [description]
        """

        xml = self.__LoadXMLTemplate('ExactAddingInvoice').format(
            DebtorNumber=self.__addleadingspaces(p_InvoiceParameters['DebtorNumber'], 20),
            Journal=p_InvoiceParameters['Journal'],
            FinancialYear=p_InvoiceParameters['FinancialYear'],
            FinancialPeriod=p_InvoiceParameters['FinancialPeriod'],
            Description=unidecode.unidecode(p_InvoiceParameters['Description']),
            TransactionKey=p_InvoiceParameters['TransactionKey']
        )

        result = self.sendToExact("/Services/Exact.Entity.Rest.EG/FinancialHeader", xml)
        if result == None:
            return False, None
        else:
            json_response = json.dumps(xmltodict.parse(result.content))
            return True, json.loads(json_response)

    def getCustomerDetailsByID(self, p_CustomerID):
        """This function returns the customer details (debtor) from Exact

        Arguments:
            p_CustomerID {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        result = self.getFromToExact(f"/Services/Exact.Entity.Rest.EG/Account/?$top=1&$filter=DebtorCode eq '{self.__addleadingspaces(p_CustomerID, 20)}'")
        if result == None:
            return False, None
        else:
            json_response = json.dumps(xmltodict.parse(result.content))
            return True, json.loads(json_response)

    def getCustomerInvoice(self, p_InvoiceID):
        result = self.getFromToExact(f"/Services/Exact.Entity.Rest.EG/FinancialLine/?$top=1&$filter=EntryNumber eq '{p_InvoiceID}'")
        if result == None:
            return None

        else:
            return result

        pass

    def getCustomerInvoiceLines(self, p_InvoiceID):
        result = self.getFromToExact(f"/Services/Exact.Entity.Rest.EG/FinancialLine/?$top=10&orderby=FinancialYear desc")
        if result == None:
            return None

        else:
            return result

        pass

    def __addleadingspaces(self, p_Input, p_Length):
        """ Add spaces to a text string.

        Arguments:
            p_Input {[type]} -- [description]
            p_Length {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        output = str(p_Input)
        while len(output) < p_Length:
            output = (f' {output}')

        return output

    def __LoadXMLTemplate(self, p_XMLFile):
        """ Loading the correct XML file

        Arguments:
            p_XMLFile {[string]} -- [Entity from the correct xml file]

        Returns:
            [string] -- [return a XML string]
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.abspath(os.path.join(current_dir, 'xml/' + p_XMLFile + '.xml'))
        with open(file_path, 'r') as xml_file:
            return xml_file.read()
