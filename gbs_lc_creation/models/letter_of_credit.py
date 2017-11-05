from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

import datetime


class LetterOfCredit(models.Model):
    _name = 'letter.credit'
    _description = 'Letter of Credit (L/C)'
    _inherit = ['mail.thread']
    _order = "issue_date desc"

    #_rec_name='name'

    # Import -> Applicant(Samuda)

    name = fields.Char(string='Number', required=True, index=True)
    type = fields.Selection([
        ('export', 'Export'),
        ('import', 'Import'),
    ], string="LC Type",
        help="Export: Product Export.\n"
             "Import: Product Import.", default="import")

    region_type = fields.Selection([
        ('local', 'Local'),
        ('foreign', 'Foreign'),
    ], string="LC Region Type",
        help="Local: Local LC.\n"
             "Foreign: Foreign LC.", default="foreign")

    first_party = fields.Many2one('res.company', string='Candidate', required=True)
    first_party_bank = fields.Many2one('res.bank', string='Bank', required=True)

    second_party = fields.Many2one('res.partner', domain=[('customer', '=', True)], string='Candidate', required=True)
    second_party_bank = fields.Text(string='Bank', required=True)

    require_lien = fields.Boolean(string='Require Lien', readonly=True, default=False)
    lien_bank = fields.Text(string='LC Lien Bank')
    lien_date = fields.Date('LC Lien Date')

    lc_value = fields.Integer(string='LC Value', readonly=True, states={'confirm': [('readonly', False)]}, required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)

    insurance_company_name = fields.Char(string='Insurance Company Name')
    insurance_number = fields.Char(string='Insurance Number')
    insurance_bill = fields.Float(string='Insurance Bill')

    landing_port = fields.Char(string='Landing Port')
    discharge_port = fields.Char(string='Discharge Port')
    cnf_agent = fields.Char(string='C&F Agent')

    issue_date = fields.Date('Issue Date', required=True)
    expiry_date = fields.Date('Expiry Date', required=True)
    shipment_date = fields.Date('Shipment Date', required=True)

    master_lc_number = fields.Char(string='Master LC Number')
    hs_code = fields.Char(string='HS Code')
    tolerance = fields.Float(string='Tolerance (%)')## 10% plus and minus value
    payment_terms = fields.Char(string='Payment Terms')
    period_of_presentation = fields.Float(string='Period of Presentation')
    ship_mode = fields.Char(string='Ship Mode')
    inco_terms = fields.Many2one('stock.incoterms',string='Inco Terms')
    partial_shipment = fields.Boolean(string='Allow Partial Shipment')
    trans_shipment =  fields.Boolean(string='Allow Trans. Shipment')
    lc_mode = fields.Char(string='LC Mode')
    terms_condition = fields.Text(string='Terms of Condition')
    remarks = fields.Text(string='Remarks')

    attachment_ids = fields.One2many('commercial.attachment', 'lc_id', string='Attachment')




    state = fields.Selection([
        ('confirm', "Confirm"),
        ('approve', "Approved")
    ], default='confirm')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'This Number is already in use')
    ]

    @api.multi
    def action_confirm(self):
        self.state = 'approve'

class CommercialAttachment(models.Model):
    _name = 'commercial.attachment'
    _description = 'Attachment'

    title = fields.Char(string='Title', required=True)
    file = fields.Binary(default='Attachment', required=True)
    lc_id = fields.Many2one("letter.credit", string='LC Number')