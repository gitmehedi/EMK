from zeep import Client

from odoo import exceptions, models, fields, api, _, tools


# url = "http://www.soapclient.com/xml/soapresponder.wsdl"
url = "http://www.soapclient.com/xml/soapresponder.wsdl"
url2 = "https://www.w3.org/2003/05/soap-envelope/"
url2 = "http://my-endpoint.com/production.svc?wsdl"


class SOAPRequest(models.Model):
    _name='soap.request.response'

    def soap_request(self):
        url2 = "http://192.168.44.94:9680/GenericTransferAmount/GenericTransferAmountInterfaceHttpService?wsdl"
        url = "http://www.soapclient.com/xml/soapresponder.wsdl"
        soap_res = Client(wsdl=url)
        # soap_res.service.Method1('Zeep','is value')
        print(soap_res.service.Method1('Zeep', 'is value'))
        print(soap_res.service.Method1('', ''))



        # with client.settings(raw_response=True):
        #     response = client.service.myoperation()
        #
        #     # response is now a regular requests.Response object
        #     assert response.status_code == 200
        #     assert response.content



