from zeep import Client

url = "http://www.soapclient.com/xml/soapresponder.wsdl"
url2 = "https://www.w3.org/2003/05/soap-envelope/"
url2 = "http://my-endpoint.com/production.svc?wsdl"

soap_res = Client(url)
tut_res = Client(url2)
 # = Client(url2)


print soap_res
