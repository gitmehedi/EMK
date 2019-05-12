from zeep import Client, Settings
import requests, urlparse, urllib, os

from odoo import exceptions, models, fields, api, _, tools

import suds
from datetime import datetime

# from suds.client import Client as s_client

# url = "http://www.soapclient.com/xml/soapresponder.wsdl"
url = "http://www.soapclient.com/xml/soapresponder.wsdl"
url2 = "https://www.w3.org/2003/05/soap-envelope/"
url2 = "http://my-endpoint.com/production.svc?wsdl"


class SOAPProcess(models.Model):
    _name = 'soap.process'
    _inherit = ["mail.thread"]
    _rec_name = 'name'
    _description = 'SOAP Endpoint'

    name = fields.Char(string='Endpoint Full Name', required=True)
    endpoint_fullname = fields.Char(string='Endpoint', compute='_compute_endpoint_fullname', store=True)

    endpoint_url = fields.Char(string='Host IP', size=24, required=True, track_visibility='onchange')
    endpoint_port = fields.Char(string='Host Port', size=10, required=True, track_visibility='onchange')
    wsdl_name = fields.Char(string='WSDL', size=100, required=True, track_visibility='onchange')
    status = fields.Boolean(string='Status', default=True)

    @api.constrains('name', 'endpoint_fullname')
    def _check_unique_constrain(self):
        if self.name or self.endpoint_fullname:
            name = self.search([('name', '=ilike', self.name.strip())])
            endpoint_fullname = self.search([('name', '=ilike', self.endpoint_fullname)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')
            if len(endpoint_fullname) > 1:
                raise Warning('[Unique Error] Endpoint must be unique!')

    @api.onchange("name", "endpoint_url", "endpoint_port", "wsdl_name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()
        if self.endpoint_url:
            self.endpoint_url = self.endpoint_url.strip()
        if self.endpoint_port:
            self.endpoint_port = self.endpoint_port.strip()
        if self.wsdl_name:
            self.wsdl_name = self.wsdl_name.strip()

    @api.depends("endpoint_url", "endpoint_port", "wsdl_name")
    def _compute_endpoint_fullname(self):
        for rec in self:
            if rec.endpoint_url and rec.endpoint_port and rec.wsdl_name:
                rec.endpoint_fullname = rec.endpoint_url + ':' + rec.endpoint_port + rec.wsdl_name

    @api.model
    def soap_request(self):

        # url = urlparse.urljoin('file:',
        #                        urllib.pathname2url(os.path.abspath("GenericTransferAmountInterfaceHttpService.wsdl")))
        url = urlparse.urljoin('file:',
                               "/opt/odoo/custom/10.0/mtbl/file_processing/models/GenericTransferAmountInterfaceHttpService.wsdl")
        # wsdl = "http://124.109.105.40:9680/GenericTransferAmount/GenericTransferAmountInterfaceHttpService?wsdl"
        # s_url = "http://obiee.banrep.gov.co/analytics/saw.dll?wsdl"
        # o_client = Client(s_url, service="SAWSessionService")
        # s_session_id = o_client.service.logon("publico", "publico")
        # o_client.set_options(service="XmlViewService")
        # transport.get(address='http://localhost:9680/soap/?wsdl', message=body, headers=headers)

        headers = {'content-type': 'text/xml'}
        body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v1="http://BaNCS.TCS.com/webservice/GenericTransferAmountInterface/v1" xmlns:ban="http://TCS.BANCS.Adapter/BANCSSchema">
   <soapenv:Header/>
   <soapenv:Body>
      <v1:genericTransferAmount>
         <!--Optional:-->
         <GenericAmtXferRq>
           <ban:RqHeader>
             <ban:InstNum>003</ban:InstNum>
               <ban:BrchNum>41101</ban:BrchNum>
               <ban:TellerNum>1101</ban:TellerNum>
               <ban:Flag4>W</ban:Flag4>
               <ban:Flag5>Y</ban:Flag5>
               <ban:UUIDSource>OGL</ban:UUIDSource>
               <ban:UUIDNUM></ban:UUIDNUM>
               <!--Optional:-->
               <ban:UUIDSeqNo></ban:UUIDSeqNo>
            </ban:RqHeader>
            <ban:Data>
               <ban:FrmAcct>1200000100009301590</ban:FrmAcct>
               <ban:Amt>111</ban:Amt>
               <ban:ToAcct>00000009788900065</ban:ToAcct>
               <!--Optional:-->
               <ban:StmtNarr>TEST OGL TXN</ban:StmtNarr>
            </ban:Data>
         </GenericAmtXferRq>
      </v1:genericTransferAmount>
   </soapenv:Body>
</soapenv:Envelope>"""
        response_body = """
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
   <soap:Body>
      <ns3:genericTransferAmountResponse xmlns:ns2="http://TCS.BANCS.Adapter/BANCSSchema" xmlns:ns3="http://BaNCS.TCS.com/webservice/GenericTransferAmountInterface/v1">
         <GenericAmtXferRs>
            <ns2:RsHeader>
               <ns2:Filler1>0</ns2:Filler1>
               <ns2:MsgLen>0</ns2:MsgLen>
               <ns2:Filler2>00</ns2:Filler2>
               <ns2:MsgTyp>0</ns2:MsgTyp>
               <ns2:Filler3>78</ns2:Filler3>
               <ns2:CycNum>0</ns2:CycNum>
               <ns2:MsgNum>0</ns2:MsgNum>
               <ns2:SegNum>0</ns2:SegNum>
               <ns2:FrntEndNum>0</ns2:FrntEndNum>
               <ns2:TermlNum>9047</ns2:TermlNum>
               <ns2:InstNum>3</ns2:InstNum>
               <ns2:BrchNum>6</ns2:BrchNum>
               <ns2:WorkstationNum>48</ns2:WorkstationNum>
               <ns2:TellerNum>1101</ns2:TellerNum>
               <ns2:TrnNum>034038</ns2:TrnNum>
               <ns2:JrnlNum>6421</ns2:JrnlNum>
               <ns2:RsHdrDt>0804</ns2:RsHdrDt>
               <ns2:Filler4>2</ns2:Filler4>
               <ns2:Filler5>0</ns2:Filler5>
               <ns2:Filler6>19</ns2:Filler6>
               <ns2:Flag1>0</ns2:Flag1>
               <ns2:Flag2>2</ns2:Flag2>
               <ns2:Flag3>0</ns2:Flag3>
               <ns2:Flag4>0</ns2:Flag4>
               <ns2:Filler9>00000000        000000000000000000000000000000OGL                                0000</ns2:Filler9>
               <ns2:OutputType>08</ns2:OutputType>
            </ns2:RsHeader>
            <ns2:Stat>
               <ns2:OkMessage>
                  <ns2:RcptData>O.K.</ns2:RcptData>
                  <ns2:Filler2>O.K.</ns2:Filler2>
                  <ns2:CustNum/>
                  <ns2:Filler1>0000</ns2:Filler1>
                  <ns2:AcctNum/>
               </ns2:OkMessage>
            </ns2:Stat>
         </GenericAmtXferRs>
      </ns3:genericTransferAmountResponse>
   </soap:Body>
</soap:Envelope>
        """
        endpoint = self.search([('name', '=', 'Generic Transfer')], limit=1)
        # settings = Settings(extra_http_headers={'content-type': 'text/xml'})
        # settings = Settings(extra_http_headers='get')
        # res = Client(endpoint.endpoint_fullname, settings=settings)
        # res.service.get_stock_quantity(2)
        if len(endpoint) > 0:
            response = requests.get(endpoint.endpoint_fullname, data=body, headers=headers)
            print(response.content)

            # url = "http://www.soapclient.com/xml/soapresponder.wsdl"
            # soap_res = Client(wsdl=endpoint.endpoint_fullname)
            # soap_res.service.Method1('Zeep','is value')
            # print(soap_res.service.Method1('Zeep', 'is value'))
            # print(soap_res.service.Method1('', ''))

            # with client.settings(raw_response=True):
            #     response = client.service.myoperation()
            #
            #     # response is now a regular requests.Response object
            #     assert response.status_code == 200
            #     assert response.content
