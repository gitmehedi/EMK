import requests, json

from odoo import exceptions, models, fields, api, _, tools
from xml.etree import ElementTree


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
        endpoint = self.search([('name', '=', 'GenericTransferAmountInterfaceHttpService')], limit=1)
        genericTransfer = 'http://124.109.105.40:9680/GenericTransferAmount/GenericTransferAmountInterfaceHttpService?wsdl'
        headers = {'content-type': 'application/soap+xml'}

        if len(endpoint) > 0:
            reqBody = self.genGenericTransferAmountInterface(data={})

            resBody = requests.post(endpoint.endpoint_fullname, data=reqBody, headers=headers)
            root = ElementTree.fromstring(resBody.content)
            response = {}
            for rec in root.iter('*'):
                key = rec.tag.split("}")
                text = rec.text
                if len(key) == 2:
                    response[key[1]] = text
                else:
                    response[key[0]] = text

            if 'ErrorMessage' in response:
                errors = "ErrorCode: {0}, ErrorMessage: {1}".format(response['ErrorCode'], response['ErrorMessage'],
                                                                    response['SupOverRide'])

                self.env['soap.process.error'].create(
                    {'name': endpoint.endpoint_fullname, 'errors': json.dumps(response)})

    @api.model
    def genGenericTransferAmountInterface(self, data):
        reqData = {
            'InstNum': '003',
            'BrchNum': '41101',
            'TellerNum': '1101',
            'Flag4': 'W',
            'Flag5': 'Y',
            'UUIDSource': 'OGL',
            'UUIDNUM': '',
            'UUIDSeqNo': '',
            'FrmAcct': '1200000100009301590',
            'Amt': '111',
            'ToAcct': '00000009788900065',
            'StmtNarr': 'TEST OGL TXNF',

        }
        requestSOAP = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v1="http://BaNCS.TCS.com/webservice/GenericTransferAmountInterface/v1" xmlns:ban="http://TCS.BANCS.Adapter/BANCSSchema">
           <soapenv:Header/>
           <soapenv:Body>
              <v1:genericTransferAmount>
                 <!--Optional:-->
                 <GenericAmtXferRq>
                   <ban:RqHeader>
                     <ban:InstNum>{0}</ban:InstNum>
                       <ban:BrchNum>{1}</ban:BrchNum>
                       <ban:TellerNum>{2}</ban:TellerNum>
                       <ban:Flag4>{0}</ban:Flag4>
                       <ban:Flag5>{0}</ban:Flag5>
                       <ban:UUIDSource>{0}</ban:UUIDSource>
                       <ban:UUIDNUM>{0}</ban:UUIDNUM>
                       <!--Optional:-->
                       <ban:UUIDSeqNo>{0}</ban:UUIDSeqNo>
                    </ban:RqHeader>
                    <ban:Data>
                       <ban:FrmAcct>{0}</ban:FrmAcct>
                       <ban:Amt>{0}</ban:Amt>
                       <ban:ToAcct>{0}</ban:ToAcct>
                       <!--Optional:-->
                       <ban:StmtNarr>{0}</ban:StmtNarr>
                    </ban:Data>
                 </GenericAmtXferRq>
              </v1:genericTransferAmount>
           </soapenv:Body>
        </soapenv:Envelope>""".format(reqData['InstNum'], reqData['BrchNum'], reqData['TellerNum'], reqData['Flag4'],
                                      reqData['Flag5'], reqData['UUIDSource'], reqData['UUIDNUM'], reqData['UUIDSeqNo'],
                                      reqData['FrmAcct'], reqData['Amt'], reqData['ToAcct'], reqData['StmtNarr'])
        return requestSOAP
