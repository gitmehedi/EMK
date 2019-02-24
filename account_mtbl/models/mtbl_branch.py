from odoo import api, fields, models,_

class Branch(models.Model):
    _name = 'operating.unit'
    _inherit = ['operating.unit','mail.thread']

    code = fields.Char('Code', required=True, size=3,track_visibility='onchange')
    name = fields.Char('Name', required=True,track_visibility='onchange')
    active = fields.Boolean('Active', default=True,track_visibility='onchange')
    company_id = fields.Many2one(
        'res.company', 'Company', required=True, track_visibility='onchange',default=lambda self:
        self.env['res.company']._company_default_get('account.account'))
    partner_id = fields.Many2one('res.partner', 'Partner', required=True,track_visibility='onchange')
    branch_type = fields.Selection([('metro', 'Metro'), ('urban', 'Urban'),('rural','Rural')],
                                string='Branch Type', track_visibility='onchange')
