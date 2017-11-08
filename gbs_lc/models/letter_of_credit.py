from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError
from openerp.addons.commercial.models.utility import Status, UtilityNumber


class LetterOfCredit(models.Model):
    _name = 'letter.credit'
    _description = 'Letter of Credit (L/C)'
    _inherit = ['mail.thread']
    _order = "issue_date desc"

    #_rec_name='name'

    # Import -> Applicant(Samuda)

    name = fields.Char(string='LC Number', index=True,readonly=True)
    title = fields.Text(string='LC Head', required=True)

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

    require_lien = fields.Boolean(string='Require Lien', default=False)
    lien_bank = fields.Text(string='LC Lien Bank')
    lien_date = fields.Date('LC Lien Date')

    lc_value = fields.Integer(string='LC Value', readonly=False, states={'approved': [('readonly', True)]}, track_visibility='onchange', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', track_visibility='onchange')

    insurance_company_name = fields.Char(string='Insurance Company Name')
    insurance_number = fields.Char(string='Insurance Number')
    insurance_bill = fields.Float(string='Insurance Bill')

    landing_port = fields.Char(string='Landing Port', track_visibility='onchange')
    discharge_port = fields.Char(string='Discharge Port', track_visibility='onchange')
    cnf_agent = fields.Char(string='C&F Agent', track_visibility='onchange')

    issue_date = fields.Date('Issue Date', track_visibility='onchange')
    expiry_date = fields.Date('Expiry Date', track_visibility='onchange')
    shipment_date = fields.Date('Shipment Date', track_visibility='onchange')

    master_lc_number = fields.Char(string='Master LC Number', track_visibility='onchange')
    hs_code = fields.Char(string='HS Code', track_visibility='onchange')
    tolerance = fields.Float(string='Tolerance (%)', track_visibility='onchange')## 10% plus and minus value
    payment_terms = fields.Char(string='Payment Terms', track_visibility='onchange')
    period_of_presentation = fields.Float(string='Period of Presentation', track_visibility='onchange')
    ship_mode = fields.Char(string='Ship Mode', track_visibility='onchange')
    inco_terms = fields.Many2one('stock.incoterms',string='Inco Terms', track_visibility='onchange')
    partial_shipment = fields.Boolean(string='Allow Partial Shipment', track_visibility='onchange')
    trans_shipment =  fields.Boolean(string='Allow Trans. Shipment', track_visibility='onchange')
    lc_mode = fields.Char(string='LC Mode', track_visibility='onchange')
    terms_condition = fields.Text(string='Terms of Condition')
    remarks = fields.Text(string='Remarks')

    attachment_ids = fields.One2many('ir.attachment', 'res_id', string='Attachments')

    state = fields.Selection([
        ('draft', "Draft"),
        ('open', "Open"),
        ('confirmed', "Confirmed"),
        ('amendment', "Amendment"),
        ('progress', "In Progress"),
        ('done', "Done")
    ], default='draft')

    last_note = fields.Char(string='Step', track_visibility='onchange')

    @api.multi
    def unlink(self):
        for lc in self:
            if str(lc.state) != 'draft' and str(lc.state) != 'open':
                raise UserError('You can not delete this.')
            else:
                return super(LetterOfCredit, self).unlink()


    @api.multi
    def action_open(self):
        self.write({'state': 'open','last_note': Status.OPEN.value})

    @api.multi
    def action_confirm(self):
        res = self.env.ref('gbs_lc.lc_number_wizard')
        result = {
            'name': _('Please Give The Number Of LC'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'lc.number.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.one
    @api.constrains('name')
    def _check_name(self):
        domain = ['&','&','|',('name', '=', self.name),
                  ('type','=',self.type),
                  ('id', '=', False),
                  ('id', '!=', self.id)]
        if self.search_count(domain):
            raise UserError('You can\'t create duplicate Number')
        return True

# class CommercialAttachment(models.Model):
#     _name = 'commercial.attachment'
#     _description = 'Attachment'
#
#     title = fields.Char(string='Title', required=True)
#     file = fields.Binary(default='Attachment', required=True)
#     lc_id = fields.Many2one("letter.credit", string='LC Number', ondelete='cascade')



