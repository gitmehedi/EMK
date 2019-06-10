import requests, json

from odoo import exceptions, models, fields, api, _, tools
from xml.etree import ElementTree


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
    def apiInterfaceMapping(self, debit, credit):
        if debit == 1 and credit == 1:
            endpoint = self.search([('name', '=', 'GenericTransferAmountInterfaceHttpService')], limit=1)
            if endpoint:
                return endpoint
        elif debit == 1 and credit > 1:
            endpoint = self.search([('name', '=', 'SingleDebitMultiCreditInterfaceHttpService')], limit=1)
            if endpoint:
                return endpoint
        else:
            return {}

    @api.model
    def prepare_bgl(self, record, rec):
        sub_operating_unit = rec.sub_operating_unit_id.code if rec.sub_operating_unit_id else '001'
        return "0{0}{1}00{2}".format(rec.account_id.code, sub_operating_unit, record.operating_unit_id.code)

    @api.model
    def action_api_interface(self):
        pending_journal = self.env['account.move'].search([('is_sync', '=', False), ('is_cbs', '=', False)])
        for record in pending_journal:
            debit, credit = 0, 0
            for rec in record.line_ids:
                if rec.debit > 0:
                    debit += 1
                if rec.credit > 0:
                    credit += 1
            endpoint = self.apiInterfaceMapping(debit, credit)

            if endpoint:
                if endpoint.name == 'GenericTransferAmountInterfaceHttpService':
                    reqBody = self.genGenericTransferAmountInterface(record)
                elif endpoint.name == 'SingleDebitMultiCreditInterfaceHttpService':
                    reqBody = self.SingleDebitMultiCreditInterfaceHttpService(record)

                resBody = requests.post(endpoint.endpoint_fullname, data=reqBody,
                                        headers={'content-type': 'application/text'})
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
                    error = {
                        'name': endpoint.endpoint_fullname,
                        'request_body': reqBody,
                        'response_body': resBody.content,
                        'error_code': response['ErrorCode'],
                        'error_message': response['ErrorMessage'],
                        'errors': json.dumps(response)
                    }

                    self.env['soap.process.error'].create(error)
                else:
                    record.write({'is_sync': True})

    @api.model
    def action_payment_instruction(self):
        payment_instruction = self.env['payment.instruction'].search([('is_sync', '=', False)])
        for record in payment_instruction:
            debit, credit = 1, 1
            endpoint = self.apiInterfaceMapping(debit, credit)

            if endpoint:
                reqBody = self.genGenericTransferAmountInterface(record)
                resBody = requests.post(endpoint.endpoint_fullname, data=reqBody,
                                        headers={'content-type': 'application/text'})
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
                    error = {
                        'name': endpoint.endpoint_fullname,
                        'request_body': reqBody,
                        'response_body': resBody.content,
                        'error_code': response['ErrorCode'],
                        'error_message': response['ErrorMessage'],
                        'errors': json.dumps(response)
                    }

                    self.env['soap.process.error'].create(error)
                else:
                    record.write({'is_sync': True})

    @api.model
    def genGenericTransferAmountInterface(self, record):
        creStr = ""
        for rec in record.line_ids:
            bgl = self.prepare_bgl(record, rec)
            # bgl1 = '01350100100100001'
            # bgl2 = '01350100100100002'
            if rec.debit > 0:
                creStr = creStr + """\n<ban:FrmAcct>{0}</ban:FrmAcct>""".format(bgl)
            elif rec.credit > 0:
                creStr = """<ban:Amt>{0}</ban:Amt>
                       <ban:ToAcct>{1}</ban:ToAcct>
                       <ban:StmtNarr>{2}</ban:StmtNarr>""".format(rec.debit, bgl, 'TEST OGL TXNF') + creStr

        data = {
            'InstNum': '003',
            'BrchNum': str(record.operating_unit_id.code),
            'TellerNum': '1107',
            'Flag4': 'W',
            'Flag5': 'Y',
            'UUIDSource': 'OGL',
            'UUIDNUM': str(record.name),
            'UUIDSeqNo': '003',
        }
        request = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v1="http://BaNCS.TCS.com/webservice/GenericTransferAmountInterface/v1" xmlns:ban="http://TCS.BANCS.Adapter/BANCSSchema">
               <soapenv:Header/>
               <soapenv:Body>
                  <v1:genericTransferAmount>
                     <!--Optional:-->
                     <GenericAmtXferRq>
                       <ban:RqHeader>
                         <ban:InstNum>{0}</ban:InstNum>
                           <ban:BrchNum>{1}</ban:BrchNum>
                           <ban:TellerNum>{2}</ban:TellerNum>
                           <ban:Flag4>{3}</ban:Flag4>
                           <ban:Flag5>{4}</ban:Flag5>
                           <ban:UUIDSource>{5}</ban:UUIDSource>
                           <ban:UUIDNUM>{6}</ban:UUIDNUM>
                           <ban:UUIDSeqNo>{7}</ban:UUIDSeqNo>
                        </ban:RqHeader>
                        <ban:Data>
                           {8}
                        </ban:Data>
                     </GenericAmtXferRq>
                  </v1:genericTransferAmount>
               </soapenv:Body>
            </soapenv:Envelope>""".format(data['InstNum'], data['BrchNum'], data['TellerNum'], data['Flag4'],
                                          data['Flag5'], data['UUIDSource'], data['UUIDNUM'], data['UUIDSeqNo'],
                                          creStr)
        return request

    @api.model
    def SingleDebitMultiCreditInterfaceHttpService(self, record):
        creStr = ""
        for rec in record.line_ids:
            bgl = self.prepare_bgl(record, rec)
            if rec.credit > 0:
                creStr = creStr + """<ban:Coll>
                                          <ban:BnfcryAcctNum>{0}</ban:BnfcryAcctNum>
                                          <ban:CrAmt>{1}</ban:CrAmt>
                                       </ban:Coll>""".format(bgl, rec.credit)
            elif rec.debit > 0:
                currency = rec.currency_id.code if rec.currency_id else ''
                creStr = """<ban:AcctNum>{0}</ban:AcctNum>
                                   <ban:Amt>{1}</ban:Amt>
                                   <ban:AcctCur>{2}</ban:AcctCur>
                                   <ban:Sys>DEP</ban:Sys>
                                   <ban:Comsn>0</ban:Comsn>""".format(bgl, rec.debit, currency) + creStr
        data = {
            'InstNum': '003',
            'BrchNum': record.operating_unit_id.code,
            'TellerNum': '1101',
            'Flag4': 'W',
            'Flag5': 'Y',
            'UUIDSource': 'OGL',
            'UUIDNUM': '',
            'UUIDSeqNo': '',

        }
        requests = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v1="http://BaNCS.TCS.com/webservice/SingleDebitMultiCreditInterface/v1" xmlns:ban="http://TCS.BANCS.Adapter/BANCSSchema">
                       <soapenv:Header/>
                       <soapenv:Body>
                          <v1:singleDebitMultiCredit>
                             <!--Optional:-->
                             <SnglDrMultCrRq>
                                <ban:RqHeader>
                                   <ban:InstNum>{0}</ban:InstNum>
                                   <ban:BrchNum>{1}</ban:BrchNum>
                                   <ban:TellerNum>{2}</ban:TellerNum>
                                   <ban:Flag4>{3}</ban:Flag4>
                                   <ban:Flag5>{4}</ban:Flag5>
                                   <ban:UUIDSource>{5}</ban:UUIDSource>
                                   <ban:UUIDNUM>{6}</ban:UUIDNUM>
                                   <!--Optional:-->
                                   <ban:UUIDSeqNo>{7}</ban:UUIDSeqNo>
                                </ban:RqHeader>
                                <ban:Data>
                                   {8}
                                </ban:Data>
                             </SnglDrMultCrRq>
                          </v1:singleDebitMultiCredit>
                       </soapenv:Body>
                    </soapenv:Envelope>""".format(data['InstNum'], data['BrchNum'], data['TellerNum'], data['Flag4'],
                                                  data['Flag5'], data['UUIDSource'], data['UUIDNUM'], data['UUIDSeqNo'],
                                                  creStr)
        # return requests
        return """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v1="http://BaNCS.TCS.com/webservice/SingleDebitMultiCreditInterface/v1" xmlns:ban="http://TCS.BANCS.Adapter/BANCSSchema">
   <soapenv:Header/>
   <soapenv:Body>
      <v1:singleDebitMultiCredit>
         <!--Optional:-->
         <SnglDrMultCrRq>
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
               <ban:AcctNum>100009298327</ban:AcctNum>
               <ban:Amt>500</ban:Amt>
               <!--Optional:-->
               <ban:AcctCur>BDT</ban:AcctCur>
               <ban:Sys>DEP</ban:Sys>
               <!--Optional:-->
               <ban:Comsn>0</ban:Comsn>
               <!--Zero or more repetitions:-->
               <ban:Coll>
                  <ban:BnfcryAcctNum>100009297549</ban:BnfcryAcctNum>
                  <ban:CrAmt>500</ban:CrAmt>
               </ban:Coll>
            </ban:Data>
         </SnglDrMultCrRq>
      </v1:singleDebitMultiCredit>
   </soapenv:Body>
</soapenv:Envelope>"""
