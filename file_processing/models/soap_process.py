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
    def action_api_interface(self):
        pending_journal = self.env['account.move'].search(
            [('is_sync', '=', False), ('is_cbs', '=', False), ('state', '=', 'posted')])

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
                elif endpoint.name == 'AccountingEntryMDMCInterfaceHttpService':
                    reqBody = self.AccountingEntryMDMCInterfaceHttpService(record)

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
                elif 'OkMessage' in response:
                    record.write({'is_sync': True})
                elif 'faultcode' in response:
                    error = {
                        'name': endpoint.endpoint_fullname,
                        'request_body': reqBody,
                        'response_body': resBody.content,
                        'error_code': response['faultcode'],
                        'error_message': response['faultstring'],
                        'errors': json.dumps(response)
                    }
                    self.env['soap.process.error'].create(error)

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
            endpoint = self.search([('name', '=', 'AccountingEntryMDMCInterfaceHttpService')], limit=1)
            if endpoint:
                return endpoint

    @api.model
    def genGenericTransferAmountInterface(self, record):
        creStr = ""
        for rec in record.line_ids:
            bgl = self.prepare_bgl(record, rec)
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
            'UUIDSeqNo': '',
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
                           <!--Optional:-->
                           <ban:AcctCur>{2}</ban:AcctCur>
                           <ban:Rmrk>Testing SDMC</ban:Rmrk>""".format(bgl, rec.debit, currency) + creStr
        data = {
            'InstNum': '003',
            'BrchNum': str('00' + record.operating_unit_id.code),
            'TellerNum': '1101',
            'Flag4': 'W',
            'Flag5': 'Y',
            'UUIDSource': 'OGL',
            'UUIDNUM': str(record.name),
            'UUIDSeqNo': '',

        }

        return """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v1="http://BaNCS.TCS.com/webservice/SingleDebitMultiCreditInterface/v1" xmlns:ban="http://TCS.BANCS.Adapter/BANCSSchema">
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

    @api.model
    def AccountingEntryMDMCInterfaceHttpService(self, record):
        creStr = ""
        for rec in record.line_ids:
            line = {
                'AcctNum': self.prepare_bgl(record, rec),
                'Amt': rec.credit,
                'Cur': rec.currency_id.code if rec.currency_id else '',
                'CasaGlInd': 3,
                'Narr': rec.name,
                'SeqNum': '003',
                'ValDt': self.format_date(rec.date),
                'TrnDt': self.format_date(rec.date),
                'CostCtr': rec.analytic_account_id.code if rec.analytic_account_id else '',
                'PromoNum': '',
            }
            if rec.credit > 0:
                creStr = creStr + """<ban:Coll>
                        <!--Optional:-->
                        <ban:AcctNum>{0}</ban:AcctNum>
                        <!--Optional:-->
                        <ban:DrCrInd>C</ban:DrCrInd>
                        <!--Optional:-->
                        <ban:Amt>{1}</ban:Amt>
                        <!--Optional:-->
                        <ban:Cur>{2}</ban:Cur>
                        <!--Optional:-->
                        <ban:Narr>{3}</ban:Narr>
                        <!--Optional:-->
                        <ban:CasaGlInd>{4}</ban:CasaGlInd>
                        <!--Optional:-->
                        <ban:SeqNum>{5}</ban:SeqNum>
                        <!--Optional:-->
                        <ban:ValDt>{6}</ban:ValDt>
                        <!--Optional:-->
                        <ban:TrnDt>{7}</ban:TrnDt>
                        <!--Optional:-->
                        <ban:CostCtr>{8}</ban:CostCtr>
                        <!--Optional:-->
                        <ban:PromoNum>{9}</ban:PromoNum>
                    </ban:Coll>""".format(line['AcctNum'], line['Amt'], line['Cur'], line['Narr'],
                                          line['CasaGlInd'], line['SeqNum'], line['ValDt'], line['TrnDt'],
                                          line['CostCtr'], line['PromoNum'])
            elif rec.debit > 0:
                creStr = """ <ban:Coll>
                        <!--Optional:-->
                        <ban:AcctNum>{0}</ban:AcctNum>
                        <!--Optional:-->
                        <ban:DrCrInd>D</ban:DrCrInd>
                        <!--Optional:-->
                        <ban:Amt>{1}</ban:Amt>
                        <!--Optional:-->
                        <ban:Cur>{2}</ban:Cur>
                        <!--Optional:-->
                        <ban:Narr>{3}</ban:Narr>
                        <!--Optional:-->
                        <ban:CasaGlInd>{4}</ban:CasaGlInd>
                        <!--Optional:-->
                        <ban:SeqNum>{5}</ban:SeqNum>
                        <!--Optional:-->
                        <ban:ValDt>{6}</ban:ValDt>
                        <!--Optional:-->
                        <ban:TrnDt>{7}</ban:TrnDt>
                        <!--Optional:-->
                        <ban:CostCtr>{8}</ban:CostCtr>
                        <!--Optional:-->
                        <ban:PromoNum>{9}</ban:PromoNum>
                    </ban:Coll>""".format(line['AcctNum'], line['Amt'], line['Cur'], line['Narr'],
                                          line['CasaGlInd'], line['SeqNum'], line['ValDt'], line['TrnDt'],
                                          line['CostCtr'], line['PromoNum']) + creStr
        data = {
            'InstNum': '003',
            'BrchNum': str('00' + record.operating_unit_id.code),
            'TellerNum': '1101',
            'TranNum': '1101',
            'Flag4': 'W',
            'Flag5': 'Y',

        }
        return """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v1="http://BaNCS.TCS.com/webservice/AccountingEntryMDMCInterface/v1" xmlns:ban="http://TCS.BANCS.Adapter/BANCSSchema">
                    <soapenv:Header/>
                    <soapenv:Body>
                        <v1:accountingEntryMDMC>
                            <!--Optional:-->
                            <AcctngEntryMDMCRq>
                                <ban:RqHeader>
                                   <ban:InstNum>{0}</ban:InstNum>
                                   <ban:BrchNum>{1}</ban:BrchNum>
                                   <ban:TellerNum>{2}</ban:TellerNum>
                                   <ban:TranNum>{3}</ban:TranNum>
                                   <ban:Flag4>{4}</ban:Flag4>
                                   <ban:Flag5>{5}</ban:Flag5>
                                </ban:RqHeader>
                                <ban:Data>
                                   {6}
                                </ban:Data>
                            </AcctngEntryMDMCRq>
                        </v1:accountingEntryMDMC>
                    </soapenv:Body>
                </soapenv:Envelope>""".format(data['InstNum'], data['BrchNum'], data['TellerNum'], data['TranNum'],
                                              data['Flag4'], data['Flag5'], creStr)

    @api.model
    def action_payment_instruction(self):
        payment_instruction = self.env['payment.instruction'].search([('is_sync', '=', False),('state', '=', 'approve')])
        for record in payment_instruction:
            debit, credit = 1, 1
            endpoint = self.apiInterfaceMapping(debit, credit)

            if endpoint:
                reqBody = self.genGenericTransferAmountInterfaceForPayment(record)
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
                elif 'OkMessage' in response:
                    record.write({'is_sync': True})
                elif 'faultcode' in response:
                    error = {
                        'name': endpoint.endpoint_fullname,
                        'request_body': reqBody,
                        'response_body': resBody.content,
                        'error_code': response['faultcode'],
                        'error_message': response['faultstring'],
                        'errors': json.dumps(response)
                    }
                    self.env['soap.process.error'].create(error)

    @api.model
    def genGenericTransferAmountInterfaceForPayment(self, record):
        sub_operating_unit = record.sub_operating_unit_id.code if record.sub_operating_unit_id else '001'
        from_bgl = "0{0}{1}00{2}".format(record.default_debit_account_id.code, sub_operating_unit,
                                         record.operating_unit_id.code)
        if record.vendor_bank_acc:
            to_bgl = record.vendor_bank_acc
        else:
            to_bgl = "0{0}{1}00{2}".format(record.default_credit_account_id.code, sub_operating_unit,
                                           record.operating_unit_id.code)

        data = {
            'InstNum': '003',
            'BrchNum': str('00' + record.operating_unit_id.code),
            'TellerNum': '1107',
            'Flag4': 'W',
            'Flag5': 'Y',
            'UUIDSource': 'OGL',
            'UUIDNUM': str(record.code),
            'UUIDSeqNo': '',
            'FrmAcct': from_bgl,
            'Amt': record.amount,
            'ToAcct': to_bgl,
            'StmtNarr': "Payment Instruction",
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
                           <ban:FrmAcct>{8}</ban:FrmAcct>
                           <ban:Amt>{9}</ban:Amt>
                           <ban:ToAcct>{10}</ban:ToAcct>
                           <ban:StmtNarr>{11}</ban:StmtNarr>
                        </ban:Data>
                     </GenericAmtXferRq>
                  </v1:genericTransferAmount>
               </soapenv:Body>
            </soapenv:Envelope>""".format(data['InstNum'], data['BrchNum'], data['TellerNum'], data['Flag4'],
                                          data['Flag5'], data['UUIDSource'], data['UUIDNUM'], data['UUIDSeqNo'],
                                          data['FrmAcct'], data['Amt'], data['ToAcct'], data['StmtNarr'])
        return request

    @api.model
    def prepare_bgl(self, record, rec):
        sub_operating_unit = rec.sub_operating_unit_id.code if rec.sub_operating_unit_id else '001'
        return "0{0}{1}00{2}".format(rec.account_id.code, sub_operating_unit, record.operating_unit_id.code)

    def format_date(self, val):
        vals = val.split('-')
        return vals[0] + vals[1] + vals[2]
