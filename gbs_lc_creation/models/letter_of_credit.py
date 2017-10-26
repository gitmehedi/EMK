from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

import datetime


class LetterOfCredit(models.Model):
    _name = 'letter.credit'
    _description = 'Letter of Credit (L/C)'
    _inherit = ['mail.thread']
    _rec_name='name'


    name = fields.Char(string='Name', index=True, readonly=True)
    applicant = fields.Many2one('res.partner',string='Applicant', required=True)
    issue_date = fields.Date('Issue Date', readonly=True,required=True, states={'confirm': [('readonly', False)]})
    lc_expiry_date = fields.Date('LC Expiry Date', readonly=True,required=True, states={'confirm': [('readonly', False)]})
    lc_opening_bank = fields.Char(string='LC Opening Bank', readonly=True,  states={'confirm': [('readonly', False)]})
    require_lien = fields.Boolean(string='Require Lieu', required=True,readonly=True, default=False, states={'confirm': [('readonly', False)]})
    lc_lieu_bank = fields.Text(string='LC Lieu Bank')
    lc_lieu_date = fields.Date('LC Lieu Date')
    advising_bank = fields.Text(string='Advising Bank')

    lc_value = fields.Integer(string='LC Value',  required=True, readonly=True, states={'confirm': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency',readonly=True,required=True, states={'confirm': [('readonly', False)]})
    tolerance = fields.Float(string='Tolerance (%)', required=True, readonly=True, states={'confirm': [('readonly', False)]})## 10% plus and minus value
    payment_terms = fields.Char(string='Payment Terms',readonly=True, states={'confirm': [('readonly', False)]})
    period_of_presentation = fields.Float(string='Period of Presentation', readonly=True, states={'confirm': [('readonly', False)]})
    ship_mode = fields.Char(string='Ship Mode', readonly=True, states={'confirm': [('readonly', False)]})
    inco_terms = fields.Many2one('stock.incoterms',string='Inco Terms', readonly=True, states={'confirm': [('readonly', False)]})
    partial_shipment = fields.Boolean(string='Allow Partial Shipment', readonly=True, states={'confirm': [('readonly', False)]})
    trans_shipment =  fields.Boolean(string='Allow Trans. Shipment', readonly=True, states={'confirm': [('readonly', False)]})
    shipment_date = fields.Date('Shipment Date',readonly=True, states={'confirm': [('readonly', False)]})
    lc_mode = fields.Char(string='LC Mode', readonly=True, states={'confirm': [('readonly', False)]})

    terms_condition = fields.Text(string='Terms of Condition', readonly=True, states={'confirm': [('readonly', False)]})
    remarks = fields.Text(string='Remarks', readonly=True, states={'confirm': [('readonly', False)]})

    state = fields.Selection([
        ('confirm', "Confirm"),
        ('approve', "Approved")
    ], default='confirm')

    sequence_id = fields.Char('Sequence', readonly=True)
    line_ids = fields.One2many('letter.credit.line', 'parent_id', string="Documents Required", readonly=True,states={'confirm': [('readonly', False)]})


    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('letter.credit') or '/'
        vals['name'] = seq
        return super(LetterOfCredit, self).create(vals)

    @api.multi
    def action_confirm(self):
        self.state = 'approve'

class LetterOfCreditLine(models.Model):
    _name = 'letter.credit.line'
    _description = 'Letter of Credits Line (LC Line)'

    serial_no = fields.Integer(string='Sl.')
    pending_pi = fields.Integer(string='Pending PI', required=True)
    tagged_pi = fields.Integer(string='Tagged PI')

    parent_id = fields.Many2one('letter.credit', ondelete='cascade')
