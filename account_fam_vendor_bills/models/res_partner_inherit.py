from odoo import api, fields, models, _


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'

    current_employee = fields.Char(string='Current Employer', track_visibility="onchange")
    work_title = fields.Char(string='Work Title', track_visibility="onchange")
    work_phone = fields.Char(string='Work Phone', track_visibility="onchange")
    signature_image = fields.Binary(string='Signature', track_visibility="onchange")
    gender = fields.Many2one('res.gender', string='Gender', required=True, track_visibility='onchange')
    bank_id = fields.Many2one('res.bank', string='Bank Name', track_visibility='onchange')
    branch_name = fields.Char(string='Branch Name', track_visibility='onchange')
