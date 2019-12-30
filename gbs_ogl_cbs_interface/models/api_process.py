import requests, json

from odoo import models, fields, api, _, tools, SUPERUSER_ID
from xml.etree import ElementTree
import lxml.etree as etree
from odoo.exceptions import ValidationError


class SOAPProcess(models.Model):
    _name = 'soap.process'
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _rec_name = 'name'
    _description = 'API Endpoint'

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
    flag_4 = fields.Char(string='Flag 4', required=True, track_visibility='onchange', default='W')
    flag_5 = fields.Char(string='Flag 5', required=True, track_visibility='onchange', default='Y')
    status = fields.Boolean(string='Status', default=True, track_visibility='onchange')

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
            if rec.http_method and rec.endpoint_url and rec.endpoint_port and rec.wsdl_name:
                rec.endpoint_fullname = rec.http_method + "://" + rec.endpoint_url + ':' + rec.endpoint_port + '/' + rec.wsdl_name

    @api.model
    def apiInterfaceMapping(self, debit, credit):
        endpoint = self.search([('name', '=', 'GenericTransferAmountInterfaceHttpService')], limit=1)
        if endpoint:
            return endpoint

    @api.model
    def call_payment_api(self, record):
        debit, credit = 1, 1
        endpoint = self.apiInterfaceMapping(debit, credit)

        if endpoint:
            reqBody = self.genGenericTransferAmountInterfaceForPayment(record, endpoint)
            try:
                resBody = requests.post(endpoint.endpoint_fullname, data=reqBody, verify=False,
                                        auth=(endpoint.username, endpoint.password),
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

                if 'OkMessage' in response:
                    record.write({'is_sync': True, 'cbs_response': resBody.content})
                    return "OkMessage"
                elif 'ErrorMessage' in response:
                    error = {
                        'name': endpoint.endpoint_fullname,
                        'request_body': reqBody,
                        'response_body': resBody.content,
                        'error_code': response['ErrorCode'],
                        'error_message': response['ErrorMessage'],
                        'errors': json.dumps(response)
                    }
                    self.env['soap.process.error'].create(error)
                    return error
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
                    return error
            except Exception:
                error = {
                    'name': endpoint.endpoint_fullname,
                    'error_code': "Operation Interrupted",
                    'error_message': "Please contact with authority.",
                }
                self.env['soap.process.error'].create(error)
                return error
        else:
            raise ValidationError(_("API configuration is not properly set. Please contact with authorized person."))

    @api.model
    def action_payment_instruction(self):
        payment_ids = self.env['payment.instruction'].search([('is_sync', '=', False), ('state', '=', 'approved')])
        for record in payment_ids:
            self.call_payment_api(record)

    @api.model
    def genGenericTransferAmountInterfaceForPayment(self, record, endpoint):
        credit = record.default_credit_account_id.code if record.default_credit_account_id else None
        c_ou = record.credit_operating_unit_id.code if record.credit_operating_unit_id else '00001'
        c_opu = record.credit_sub_operating_unit_id.code if record.credit_sub_operating_unit_id else '001'

        debit = record.default_debit_account_id.code if record.default_debit_account_id else None
        d_ou = record.debit_operating_unit_id.code if record.debit_operating_unit_id else '00001'
        d_opu = record.debit_sub_operating_unit_id.code if record.debit_sub_operating_unit_id else '001'

        from_bgl = "0{0}{1}00{2}".format(debit, d_opu, d_ou)

        if record.vendor_bank_acc:
            to_bgl = record.vendor_bank_acc.zfill(17)
        else:
            to_bgl = "0{0}{1}00{2}".format(credit, c_opu, c_ou)

        if record.narration:
            statement = record.code + " " + record.narration
        else:
            statement = record.code

        data = {
            'InstNum': endpoint.ins_num,
            'BrchNum': d_ou.zfill(5),
            'TellerNum': endpoint.teller_no,
            'Flag4': endpoint.flag_4,
            'Flag5': endpoint.flag_5,
            'UUIDSource': endpoint.uuid_source,
            'UUIDNUM': str(record.code),
            'UUIDSeqNo': '',
            'FrmAcct': from_bgl,
            'Amt': record.amount,
            'ToAcct': to_bgl,
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
            </soapenv:Envelope>""".format(data['InstNum'], data['BrchNum'], data['TellerNum'], data['Flag4'],
                                          data['Flag5'], data['UUIDSource'], data['UUIDNUM'], data['UUIDSeqNo'],
                                          data['FrmAcct'], data['Amt'], data['ToAcct'], data['StmtNarr'])
        return request

    @api.model
    def prepare_bgl(self, record, rec):
        sub_operating_unit = rec.sub_operating_unit_id.code if rec.sub_operating_unit_id else '001'
        branch = str("00" + record.operating_unit_id.code) if record.operating_unit_id.code else '00001'
        return "0{0}{1}00{2}".format(rec.account_id.code, sub_operating_unit, branch)

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


class PaymentInstruction(models.Model):
    _inherit = 'payment.instruction'
    _payments = []

    @api.multi
    def action_approve(self):
        payment = self.search([('id', '=', self.id), ('is_sync', '=', False), ('state', '=', 'draft')])
        if not payment:
            raise ValidationError(_("Payment Instruction [{0}] already submitted.".format(self.code)))
        if payment.state == 'draft' and not payment.is_sync and payment.code not in self._payments:
            if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
                raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))

            self.payment_remove(self.code)
            response = self.env['soap.process'].call_payment_api(payment)
            if 'error_code' in response:
                self.payment_remove(self.code)
                err_text = "Payment of {0} is not possible due to following reason:\n\n - Error Code: {1} \n - Error Message: {2}".format(
                    self.code, response['error_code'], response['error_message'])
                raise ValidationError(_(err_text))
            elif response == 'OkMessage':
                payment.write({'state': 'approved'})
                if payment.invoice_id:
                    for line in payment.invoice_id.suspend_security().move_id.line_ids:
                        if line.account_id.internal_type in ('receivable', 'payable'):
                            if line.amount_residual < 0:
                                val = -1
                            else:
                                val = 1
                            line.write({'amount_residual': ((line.amount_residual) * val) - payment.amount})
                self.payment_remove(self.code)
            else:
                self.payment_remove(self.code)
        else:
            raise ValidationError(_("Payment Instruction [{0}] is processing.".format(self.code)))

    @api.multi
    def payment_remove(self, code):
        if code in self._payments:
            self._payments.remove(code)

    @api.multi
    def invalidate_payment_cache(self):
        payments = self.search([('is_sync', '=', False), ('state', '=', 'draft')])
        for val in payments:
            if val.code in self._payments:
                self._payments.remove(val.code)
