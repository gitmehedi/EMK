from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

import datetime


class LetterOfCredit(models.Model):
    _name = 'letter.credit'
    _description = 'Letter of Credit (L/C)'
    _inherit = ['mail.thread']
    #_rec_name='name'

    # Import -> Applicant(Samuda)

    name = fields.Char(string='Number', index=True)
    type = fields.Selection([
        ('export', 'Export'),
        ('import', 'Import'),
    ], string="LC Type",
        help="Export: Product Export.\n"
             "Import: Product Import.", default="import")

    first_party = fields.Many2one('res.company', string='Candidate', required=True)
    first_party_bank = fields.Many2one('res.bank', string='Bank', required=True)

    second_party = fields.Many2one('res.partner', domain=[('customer', '=', True)], string='Candidate', required=True)
    second_party_bank = fields.Text(string='Bank', states={'confirm': [('readonly', False)]})

    require_lien = fields.Boolean(string='Require Lien', required=True, readonly=True, default=False,
                                  states={'confirm': [('readonly', False)]})
    lien_bank = fields.Text(string='LC Lien Bank', states={'confirm': [('readonly', False)]})
    lien_date = fields.Date('LC Lien Date', states={'confirm': [('readonly', False)]})

    lc_value = fields.Integer(string='LC Value', required=True, readonly=True, states={'confirm': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, required=True, states={'confirm': [('readonly', False)]})

    insurance_company_name = fields.Char(string='Insurance Company Name')
    insurance_number = fields.Char(string='Insurance Number')
    insurance_bill = fields.Float(string='Insurance Bill')

    landing_port = fields.Char(string='Landing Port')
    discharge_port = fields.Char(string='Discharge Port')
    cnf_agent = fields.Char(string='C&F Agent')

    issue_date = fields.Date('Issue Date', readonly=True,required=True, states={'confirm': [('readonly', False)]})
    expiry_date = fields.Date('Expiry Date', readonly=True,required=True, states={'confirm': [('readonly', False)]})
    shipment_date = fields.Date('Shipment Date', readonly=True, states={'confirm': [('readonly', False)]})

    master_lc_number = fields.Char(string='Master LC Number', readonly=True, states={'confirm': [('readonly', False)]})
    hs_code = fields.Char(string='HS Code')
    tolerance = fields.Float(string='Tolerance (%)', required=True, readonly=True, states={'confirm': [('readonly', False)]})## 10% plus and minus value
    payment_terms = fields.Char(string='Payment Terms',readonly=True, states={'confirm': [('readonly', False)]})
    period_of_presentation = fields.Float(string='Period of Presentation', readonly=True, states={'confirm': [('readonly', False)]})
    ship_mode = fields.Char(string='Ship Mode', readonly=True, states={'confirm': [('readonly', False)]})
    inco_terms = fields.Many2one('stock.incoterms',string='Inco Terms', readonly=True, states={'confirm': [('readonly', False)]})
    partial_shipment = fields.Boolean(string='Allow Partial Shipment', readonly=True, states={'confirm': [('readonly', False)]})
    trans_shipment =  fields.Boolean(string='Allow Trans. Shipment', readonly=True, states={'confirm': [('readonly', False)]})
    lc_mode = fields.Char(string='LC Mode', readonly=True, states={'confirm': [('readonly', False)]})
    terms_condition = fields.Text(string='Terms of Condition', readonly=True, states={'confirm': [('readonly', False)]})
    remarks = fields.Text(string='Remarks', readonly=True, states={'confirm': [('readonly', False)]})
    # body_html = fields.Text('Rich-text Contents', help="Rich-text/HTML message")
    state = fields.Selection([
        ('confirm', "Confirm"),
        ('approve', "Approved")
    ], default='confirm')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'This Number is already in use')
    ]

    # @api.model
    # def create(self, vals):
    #     seq = self.env['ir.sequence'].next_by_code('letter.credit') or '/'
    #     vals['name'] = seq
    #     return super(LetterOfCredit, self).create(vals)

    @api.multi
    def action_confirm(self):
        self.state = 'approve'
