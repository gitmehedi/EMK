# from zeep import Client
import zeep
import requests

from odoo import exceptions, models, fields, api, _, tools

import suds
from datetime import datetime
from suds.client import Client

# url = "http://www.soapclient.com/xml/soapresponder.wsdl"
url = "http://www.soapclient.com/xml/soapresponder.wsdl"
url2 = "https://www.w3.org/2003/05/soap-envelope/"
url2 = "http://my-endpoint.com/production.svc?wsdl"


class SOAPProcess(models.Model):
    _name = 'soap.process'
    _inherit = ["mail.thread"]
    _rec_name = 'name'
    _description = 'SOAP Endpoint'

    name = fields.Char(string='Endpoint Name', required=True)
    endpoint_fullname = fields.Char(string='Endpoint', compute='_compute_endpoint_fullname', store=True)

    endpoint_url = fields.Char(string='Host IP', size=24, required=True, track_visibility='onchange')
    endpoint_port = fields.Char(string='Host Port', size=10, required=True, track_visibility='onchange')
    wsdl_name = fields.Char(string='WSDL', size=100, required=True, track_visibility='onchange')
    status = fields.Boolean(string='Status', default=True)

    @api.constrains('name', 'endpoint_fullname')
    def _check_unique_constrain(self):
        if self.name or self.endpoint_fullname:
            name = [['name', '=ilike', self.name]]
            endpoint_fullname = [['name', '=ilike', self.endpoint_fullname]]
            name = self.search(name)
            endpoint_fullname = self.search(endpoint_fullname)
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
        wsdl = "http://124.109.105.40:9680/GenericTransferAmount/GenericTransferAmountInterfaceHttpService?wsdl"
        # s_url = "http://obiee.banrep.gov.co/analytics/saw.dll?wsdl"
        # o_client = Client(s_url, service="SAWSessionService")
        # s_session_id = o_client.service.logon("publico", "publico")
        # o_client.set_options(service="XmlViewService")

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
        endpoint = self.search([('name', '=', 'GenericTransfer')], limit=1)
        if len(endpoint) > 0:
            response = requests.post(endpoint.endpoint_fullname, data=body, headers=headers)
            print(response.content)

            # url = "http://www.soapclient.com/xml/soapresponder.wsdl"
            # soap_res = Client(wsdl=url)
            # soap_res.service.Method1('Zeep','is value')
            # print(soap_res.service.Method1('Zeep', 'is value'))
            # print(soap_res.service.Method1('', ''))

            # with client.settings(raw_response=True):
            #     response = client.service.myoperation()
            #
            #     # response is now a regular requests.Response object
            #     assert response.status_code == 200
            #     assert response.content
