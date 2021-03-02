import requests, json

from odoo import models, fields, api, _, tools, SUPERUSER_ID
from xml.etree import ElementTree
from odoo.exceptions import ValidationError


class APIInterface(models.Model):
    _name = 'soap.process'
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _rec_name = 'name'
    _description = 'API Endpoint'
    _gl_enquiry = []

    name = fields.Char(string='Endpoint Name', required=True)
    endpoint_fullname = fields.Char(string='Endpoint', compute='_compute_endpoint_fullname', store=True)
    endpoint_url = fields.Char(string='Host IP', size=24, required=True, track_visibility='onchange')
    endpoint_port = fields.Char(string='Host Port', size=10, required=True, track_visibility='onchange')
    wsdl_name = fields.Char(string='WSDL', size=100, required=True, track_visibility='onchange')
    http_method = fields.Selection([('http', 'http'), ('https', 'https')], string='HTTP Method', default='http',
                                   required=True, track_visibility='onchange')
    username = fields.Char(string='Username', required=True, track_visibility='onchange')
    password = fields.Char(string='Password', required=True, track_visibility='onchange')
    teller_no = fields.Char(string='Teller Number', required=True, track_visibility='onchange')
    ins_num = fields.Char(string='Institution Number', required=True, track_visibility='onchange')
    uuid_source = fields.Char(string='Source of Request', required=True, track_visibility='onchange', default='OGL')
    uuid_num = fields.Char(string='UUIDNUM', track_visibility='onchange')
    uuid_seq_no = fields.Char(string='UUIDSeqNo', track_visibility='onchange')
    wsdl_type = fields.Selection(
        [('GenericTransferAmount', 'GenericTransferAmount'), ('GLToDepositTransfer', 'GLToDepositTransfer'),
         ('GLToGLTransfer', 'GLToGLTransfer'), ('GLEnquiryPrompt', 'GLEnquiryPrompt')], string='WSDL Type',
        required=True)
    status = fields.Boolean(string='Status', default=True, track_visibility='onchange')

    msg_len = fields.Char(string='MsgLen', track_visibility='onchange')
    msg_typ = fields.Char(string='MsgTyp', track_visibility='onchange')
    cyc_num = fields.Char(string='CycNum', track_visibility='onchange')
    msg_num = fields.Char(string='MsgNum', track_visibility='onchange')
    seg_num = fields.Char(string='SegNum', track_visibility='onchange')
    seg_num2 = fields.Char(string='SegNum2', track_visibility='onchange')
    frontend_num = fields.Char(string='FrontEndNum', track_visibility='onchange')
    terml_num = fields.Char(string='TermlNum', track_visibility='onchange')
    inst_num = fields.Char(string='InstNum', track_visibility='onchange')
    brch_num = fields.Char(string='BrchNum', track_visibility='onchange')
    workstation_num = fields.Char(string='WorkstationNum', track_visibility='onchange')
    teller_num = fields.Char(string='TellerNum', track_visibility='onchange')
    tran_num = fields.Char(string='TranNum', track_visibility='onchange')
    jrnl_num = fields.Char(string='JrnlNum', track_visibility='onchange')
    hdr_dt = fields.Char(string='HdrDt', track_visibility='onchange')
    filler1 = fields.Char(string='Filler1', track_visibility='onchange')
    filler2 = fields.Char(string='Filler2', track_visibility='onchange')
    filler3 = fields.Char(string='Filler3', track_visibility='onchange')
    filler4 = fields.Char(string='Filler4', track_visibility='onchange')
    filler5 = fields.Char(string='Filler5', track_visibility='onchange')
    filler6 = fields.Char(string='Filler6', track_visibility='onchange')

    flag_1 = fields.Char(string='Flag1', track_visibility='onchange')
    flag_2 = fields.Char(string='Flag2', track_visibility='onchange')
    flag_3 = fields.Char(string='Flag3', track_visibility='onchange')
    flag_4 = fields.Char(string='Flag4', track_visibility='onchange', required=True, default='W')
    flag_5 = fields.Char(string='Flag5', track_visibility='onchange', required=True, default='Y')
    flag_6 = fields.Char(string='Flag6', track_visibility='onchange')
    flag_7 = fields.Char(string='Flag7', track_visibility='onchange')
    sprvsr_id = fields.Char(string='SprvsrID', track_visibility='onchange')
    sup_date = fields.Char(string='SupDate', track_visibility='onchange')
    checker_id1 = fields.Char(string='CheckerID1', track_visibility='onchange')
    parent_blink_jrnl_num = fields.Char(string='ParentBlinkJrnlNum', track_visibility='onchange')
    checker_id2 = fields.Char(string='CheckerID2', track_visibility='onchange')
    blink_jrnl_num = fields.Char(string='BlinkJrnlNum', track_visibility='onchange')

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

    @api.depends("http_method", "wsdl_type", "endpoint_url", "endpoint_port", "wsdl_name")
    def _compute_endpoint_fullname(self):
        for rec in self:
            if rec.http_method and rec.endpoint_url and rec.endpoint_port and rec.wsdl_type and rec.wsdl_name:
                rec.endpoint_fullname = rec.http_method + "://" + rec.endpoint_url + ':' + rec.endpoint_port + '/' + rec.wsdl_type + '/' + rec.wsdl_name

    @api.model
    def search_api(self, type):
        endpoint = self.search([('wsdl_type', '=', type)], limit=1)
        if endpoint:
            return endpoint

    @api.model
    def call_generic_transfer_amount(self, record):
        ep = self.search_api('GenericTransferAmount')

        if ep:
            req_body = self.api_generic_transfer_amount(record, ep)
            try:
                res_body = requests.post(ep.endpoint_fullname,
                                         data=req_body,
                                         verify=False,
                                         auth=(ep.username, ep.password),
                                         headers={'content-type': 'application/text'})

                root = ElementTree.fromstring(res_body.content)
                response = {}
                for rec in root.iter('*'):
                    key = rec.tag.split("}")
                    text = rec.text
                    if len(key) == 2:
                        response[key[1]] = text
                    else:
                        response[key[0]] = text

                if 'OkMessage' in response:
                    record.write({'is_sync': True, 'cbs_response': res_body.content})
                    return "OkMessage"
                elif 'ErrorMessage' in response:
                    error = {
                        'name': ep.endpoint_fullname,
                        'request_body': req_body,
                        'response_body': res_body.content,
                        'error_code': response['ErrorCode'],
                        'error_message': response['ErrorMessage'],
                        'errors': json.dumps(response)
                    }
                    self.env['soap.process.error'].create(error)
                    return error
                elif 'faultcode' in response:
                    error = {
                        'name': ep.endpoint_fullname,
                        'request_body': req_body,
                        'response_body': res_body.content,
                        'error_code': response['faultcode'],
                        'error_message': response['faultstring'],
                        'errors': json.dumps(response)
                    }
                    self.env['soap.process.error'].create(error)
                    return error
            except Exception:
                error = {
                    'name': ep.endpoint_fullname,
                    'error_code': "Operation Interrupted",
                    'error_message': "Please contact with authority.",
                }
                self.env['soap.process.error'].create(error)
                return error
        else:
            raise ValidationError(_("API configuration is not properly set. Please contact with authorized person."))

    @api.model
    def call_glto_deposit_transfer(self, record):
        ep = self.search_api('GLToDepositTransfer')

        if ep:
            req_body = self.api_glto_deposit_transfer(record, ep)
            try:
                res_body = requests.post(ep.endpoint_fullname, data=req_body, verify=False,
                                         auth=(ep.username, ep.password),
                                         headers={'content-type': 'application/text'})

                root = ElementTree.fromstring(res_body.content)
                response = {}
                for rec in root.iter('*'):
                    key = rec.tag.split("}")
                    text = rec.text
                    if len(key) == 2:
                        response[key[1]] = text
                    else:
                        response[key[0]] = text

                if 'OkMessage' in response:
                    record.write({'is_sync': True, 'cbs_response': res_body.content})
                    return "OkMessage"
                elif 'ErrorMessage' in response:
                    error = {
                        'name': ep.endpoint_fullname,
                        'request_body': req_body,
                        'response_body': res_body.content,
                        'error_code': response['ErrorCode'],
                        'error_message': response['ErrorMessage'],
                        'errors': json.dumps(response)
                    }
                    self.env['soap.process.error'].create(error)
                    return error
                elif 'faultcode' in response:
                    error = {
                        'name': ep.endpoint_fullname,
                        'request_body': req_body,
                        'response_body': res_body.content,
                        'error_code': response['faultcode'],
                        'error_message': response['faultstring'],
                        'errors': json.dumps(response)
                    }
                    self.env['soap.process.error'].create(error)
                    return error
            except Exception:
                error = {
                    'name': ep.endpoint_fullname,
                    'error_code': "Operation Interrupted",
                    'error_message': "Please contact with authority.",
                }
                self.env['soap.process.error'].create(error)
                return error
        else:
            raise ValidationError(_("API configuration is not properly set. Please contact with authorized person."))

    @api.model
    def call_glto_gl_transfer(self, record):
        ep = self.search_api('GLToGLTransfer')

        if ep:
            req_body = self.api_glto_gl_transfer(record, ep)

            try:
                res_body = requests.post(ep.endpoint_fullname, data=req_body, verify=False,
                                         auth=(ep.username, ep.password),
                                         headers={'content-type': 'application/text'})

                root = ElementTree.fromstring(res_body.content)
                response = {}
                for rec in root.iter('*'):
                    key = rec.tag.split("}")
                    text = rec.text
                    if len(key) == 2:
                        response[key[1]] = text
                    else:
                        response[key[0]] = text

                if 'OkMessage' in response:
                    record.write({'is_sync': True, 'cbs_response': res_body.content})
                    return "OkMessage"
                elif 'ErrorMessage' in response:
                    error = {
                        'name': ep.endpoint_fullname,
                        'request_body': req_body,
                        'response_body': res_body.content,
                        'error_code': response['ErrorCode'],
                        'error_message': response['ErrorMessage'],
                        'errors': json.dumps(response)
                    }
                    self.env['soap.process.error'].create(error)
                    return error
                elif 'faultcode' in response:
                    error = {
                        'name': ep.endpoint_fullname,
                        'request_body': req_body,
                        'response_body': res_body.content,
                        'error_code': response['faultcode'],
                        'error_message': response['faultstring'],
                        'errors': json.dumps(response)
                    }
                    self.env['soap.process.error'].create(error)
                    return error
            except Exception:
                error = {
                    'name': ep.endpoint_fullname,
                    'error_code': "Operation Interrupted",
                    'error_message': "Please contact with authority.",
                }
                self.env['soap.process.error'].create(error)
                return error
        else:
            raise ValidationError(_("API configuration is not properly set. Please contact with authorized person."))

    @api.model
    def call_gl_enquiry_payment(self, record):
        ep = self.search_api('GLEnquiryPrompt')

        if ep:
            req_body = self.api_gl_enquiry_prompt(record, ep)
            try:
                resp_body = requests.post(ep.endpoint_fullname, data=req_body, verify=False,
                                          auth=(ep.username, ep.password),
                                          headers={'content-type': 'application/text'})

                root = ElementTree.fromstring(resp_body.content)
                response = {}
                for rec in root.iter('*'):
                    key = rec.tag.split("}")
                    text = rec.text
                    if len(key) == 2:
                        response[key[1]] = text
                    else:
                        response[key[0]] = text

                if 'GLClassCode' in response:
                    return "OkMessage"
                else:
                    return 'error_code'
            except Exception:
                return 'error_code'
        else:
            raise ValidationError(_("API configuration is not properly set. Please contact with authorized person."))

    @api.model
    def api_generic_transfer_amount(self, rec, ep):
        dr_bgl = self.prepare_bgl(rec.default_debit_account_id.code, rec.debit_sub_operating_unit_id.code,
                                  rec.debit_operating_unit_id.code)
        if rec.vendor_bank_acc:
            cr_bgl = rec.vendor_bank_acc.zfill(17)
        else:
            cr_bgl = self.prepare_bgl(rec.default_credit_account_id.code, rec.credit_sub_operating_unit_id.code,
                                      rec.credit_operating_unit_id.code)

        branch = rec.debit_operating_unit_id.code.zfill(5)
        curr_code = rec.currency_id.code
        statement = rec.code + " " + rec.narration if rec.narration else rec.code

        data = {
            'InstNum': ep.ins_num,
            'BrchNum': ep.brch_num,
            'TellerNum': ep.teller_no,
            'Flag4': ep.flag_4,
            'Flag5': ep.flag_5,
            'UUIDSource': ep.uuid_source,
            'UUIDNUM': str(rec.code),
            'UUIDSeqNo': '',
        }
        dbody = {
            'FrmAcct': dr_bgl,
            'Amt': rec.amount,
            'ToAcct': cr_bgl,
            'StmtNarr': statement,
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
            </soapenv:Envelope>"""

        return request.format(data['InstNum'], data['BrchNum'], data['TellerNum'], data['Flag4'],
                              data['Flag5'], data['UUIDSource'], data['UUIDNUM'], data['UUIDSeqNo'],
                              dbody['FrmAcct'], dbody['Amt'], dbody['ToAcct'], dbody['StmtNarr'])

    @api.model
    def api_glto_gl_transfer(self, rec, ep):
        dr_bgl = self.prepare_bgl(rec.default_debit_account_id.code, rec.debit_sub_operating_unit_id.code,
                                  rec.debit_operating_unit_id.code)
        cr_bgl = self.prepare_bgl(rec.default_credit_account_id.code, rec.credit_sub_operating_unit_id.code,
                                  rec.credit_operating_unit_id.code)

        curr_code = rec.currency_id.code
        statement = rec.code + " " + rec.narration if rec.narration else rec.code

        dhead = {
            'InstNum': ep.ins_num,
            'BrchNum': ep.brch_num,
            'TellerNum': ep.teller_no,
            'Flag4': ep.flag_4,
            'Flag5': ep.flag_5,
            'UUIDSource': ep.uuid_source,
            'UUIDNUM': str(rec.code),
            'UUIDSeqNo': '',
        }
        dbody = {
            'AcctNum1': dr_bgl,
            'Amt1': rec.amount,
            'Descptn': statement,
            'AcctNum2': cr_bgl,
            'AccCurCode1': curr_code,
            'RefNum': str(rec.reconcile_ref),
        }
        request = """<soapenv:Envelope
                        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                        xmlns:v1="http://BaNCS.TCS.com/webservice/GLToGLTransferInterface/v1"
                        xmlns:ban = "http://TCS.BANCS.Adapter/BANCSSchema">
                        <soapenv:Header/>
                        <soapenv:Body>
                            <v1:gLToGLTransfer>
                                <!--Optional:-->
                                <GLToGLXferRq>
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
                                        <ban:AcctNum1>{8}</ban:AcctNum1>
                                        <ban:Amt1>{9}</ban:Amt1>
                                        <!--Optional:-->
                                        <ban:Descptn></ban:Descptn>
                                        <!--Optional:-->
                                        <ban:AcctNum2>{11}</ban:AcctNum2>
                                        <!--Optional:-->
                                        <ban:AccCurCode1>{12}</ban:AccCurCode1>
                                        <ban:RefNum>{13}</ban:RefNum>
                                        <!--Optional:-->
                                    </ban:Data>
                                </GLToGLXferRq>
                            </v1:gLToGLTransfer>
                        </soapenv:Body>
                    </soapenv:Envelope>"""

        return request.format(dhead['InstNum'], dhead['BrchNum'], dhead['TellerNum'], dhead['Flag4'], dhead['Flag5'],
                              dhead['UUIDSource'], dhead['UUIDNUM'], dhead['UUIDSeqNo'],
                              dbody['AcctNum1'], dbody['Amt1'], dbody['Descptn'], dbody['AcctNum2'],
                              dbody['AccCurCode1'], dbody['RefNum'])

    @api.model
    def api_glto_deposit_transfer(self, rec, ep):
        dr_bgl = self.prepare_bgl(rec.default_debit_account_id.code, rec.debit_sub_operating_unit_id.code,
                                  rec.debit_operating_unit_id.code)
        cr_bgl = rec.vendor_bank_acc.zfill(17)

        curr_code = rec.currency_id.code
        statement = rec.code + " " + rec.narration if rec.narration else rec.code

        dhead = {
            'InstNum': ep.ins_num,
            'BrchNum': ep.brch_num,
            'TellerNum': ep.teller_no,
            'Flag4': ep.flag_4,
            'Flag5': ep.flag_5,
            'UUIDSource': ep.uuid_source,
            'UUIDNUM': str(rec.code),
            'UUIDSeqNo': '',
        }
        dbody = {
            'AcctNum2': cr_bgl,
            'TrnDt': '',
            'Exchgamt': '',
            'AcctNum1': dr_bgl,
            'Descptn': statement,
            'AcctCurCode1': curr_code,
            'Amt1': rec.amount,
            'RefNum': str(rec.reconcile_ref),
        }

        request = """<soapenv:Envelope
                        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                        xmlns:v1="http://BaNCS.TCS.com/webservice/GLToDepositTransferInterface/v1"
                        xmlns:ban="http://TCS.BANCS.Adapter/BANCSSchema">
                        <soapenv:Header/>
                        <soapenv:Body>
                            <v1:gLToDepositTransfer>
                                <!--Optional:-->
                                <GLToDepXferRq>
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
                                        <ban:AcctNum2>{8}</ban:AcctNum2>
                                        <ban:TrnDt></ban:TrnDt>
                                        <ban:Exchgamt>{10}</ban:Exchgamt>
                                        <ban:AcctNum1>{11}</ban:AcctNum1>
                                        <ban:Descptn>{12}</ban:Descptn>
                                        <ban:AcctCurCode1>{13}</ban:AcctCurCode1>
                                        <ban:Amt1>{14}</ban:Amt1>
                                        <ban:RefNum>{15}</ban:RefNum>
                                    </ban:Data>
                                </GLToDepXferRq>
                            </v1:gLToDepositTransfer>
                        </soapenv:Body>
                    </soapenv:Envelope>"""

        return request.format(dhead['InstNum'], dhead['BrchNum'], dhead['TellerNum'], dhead['Flag4'],
                              dhead['Flag5'], dhead['UUIDSource'], dhead['UUIDNUM'], dhead['UUIDSeqNo'],
                              dbody['AcctNum2'], dbody['TrnDt'], dbody['Exchgamt'], dbody['AcctNum1'], dbody['Descptn'],
                              dbody['AcctCurCode1'], dbody['Amt1'], dbody['RefNum'])

    @api.model
    def api_gl_enquiry_prompt(self, rec, ep):
        bgl = self.prepare_bgl(rec.account_id.code, rec.sub_operating_unit_id.code, rec.operating_unit_id.code)
        branch = ep.brch_num

        dhead = {
            'InstNum': ep.ins_num,
            'BrchNum': branch,
            'TellerNum': str(ep.teller_no),
            'Flag4': ep.flag_4,
            'Flag5': ep.flag_5,
            'UUIDSource': ep.uuid_source,
            'UUIDNUM': bgl,
            'UUIDSeqNo': ep.uuid_seq_no,
        }
        dbody = {
            'bgl': bgl,
        }

        request = """<soapenv:Envelope
                        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                        xmlns:v1="http://BaNCS.TCS.com/webservice/GLEnquiryPromptInterface/v1"
                        xmlns:ban="http://TCS.BANCS.Adapter/BANCSSchema">
                        <soapenv:Header/>
                        <soapenv:Body>
                            <v1:gLEnquiryPrompt>
                                <!--Optional:-->
                                <GLPrmptInqRq>
                                    <ban:RqHeader>
                                        <ban:InstNum>{0}</ban:InstNum>
                                        <ban:BrchNum>{1}</ban:BrchNum>
                                        <ban:TellerNum>{2}</ban:TellerNum>
                                        <ban:Flag4>{3}</ban:Flag4>
                                        <ban:Flag5>{4}</ban:Flag5>
                                        <ban:UUIDSource></ban:UUIDSource>
                                        <ban:UUIDNUM></ban:UUIDNUM>
                                        <ban:UUIDSeqNo></ban:UUIDSeqNo>
                                    </ban:RqHeader>
                                    <ban:Data>
                                        <ban:AcctNum>{5}</ban:AcctNum>
                                        <!--Optional:-->
                                        <ban:Opt>1</ban:Opt>
                                    </ban:Data>
                                </GLPrmptInqRq>
                            </v1:gLEnquiryPrompt>
                        </soapenv:Body>
                    </soapenv:Envelope>"""

        return request.format(dhead['InstNum'], dhead['BrchNum'], dhead['TellerNum'], dhead['Flag4'],
                              dhead['Flag5'], dbody['bgl'])

    @api.model
    def action_payment_instruction(self):
        payment_ids = self.env['payment.instruction'].search([('is_sync', '=', False), ('state', '=', 'approved')])
        for record in payment_ids:
            self.call_generic_transfer_amount(record)

    @api.model
    def action_gl_enquire_process(self):
        if not self._gl_enquiry:
            self._gl_enquiry.append('active')
            mv_lines = self.env['account.move.line'].search([('is_bgl', '!=', 'pass'),
                                                             ('move_id.is_sync', '=', False),
                                                             ('move_id.is_opening', '=', False),
                                                             ('move_id.is_cbs', '=', False),
                                                             ('move_id.state', '=', 'posted')], order='id ASC')
            for mv in mv_lines:
                try:

                    response = self.call_gl_enquiry_payment(mv)
                    if 'error_code' in response:
                        mv.write({'is_bgl': 'fail'})
                    elif response == 'OkMessage':
                        mv.write({'is_bgl': 'pass'})
                except Exception:
                    pass

            self._gl_enquiry.remove('active')

    @api.model
    def prepare_bgl(self, account, seq, branch):
        return '{0}{1}{2}'.format(account.zfill(9), seq.zfill(3), branch.zfill(5))

    def format_date(self, val):
        vals = val.split('-')
        return vals[0] + vals[1] + vals[2]

    @api.model
    def _needaction_domain_get(self):
        return [('status', '=', True)]


class ServerFileError(models.Model):
    _name = 'soap.process.error'
    _description = "SOAP Processing Error"
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _order = 'id desc'

    name = fields.Char(string='Title', required=True)
    process_date = fields.Datetime(string='Process Date', default=fields.Datetime.now, required=True, readonly=True)
    status = fields.Boolean(default=False, string='Status')
    request_body = fields.Text(string='Request Data')
    response_body = fields.Text(string='Response Data')
    errors = fields.Text(string='Error Code')
    error_code = fields.Char(string='Error Code', required=True)
    error_message = fields.Char(string='Error Details', required=True)
    state = fields.Selection([('issued', 'Issued'), ('resolved', 'Resolved')], default='issued')

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'issued')]
