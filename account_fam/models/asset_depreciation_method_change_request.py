from odoo import api, fields, models, _


class AssetDepreciationMethodChangeRequest(models.Model):
    _name = 'asset.depreciation.method.change.request'
    _inherit = ['mail.thread']
    _description = 'Asset Depreciation Method Change Request'
    _order = 'name desc'

    name = fields.Char(required=False, track_visibility='onchange', string='Name', default='/')
    asset_cat_id = fields.Many2one('account.asset.category', track_visibility='onchange', required=True,
                                   domain=[('parent_id', '!=', False)], string='Asset Category')
    method = fields.Selection([
        ('linear', 'Straight Line/Linear')
        ], default='linear', string="Method",
        track_visibility='onchange', readonly=True)
    asset_life = fields.Float('Asset Life')
    narration = fields.Text('Narration')
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirmed"),
        ('approve', "Approved"),
        ('cancel', "Canceled")], default='draft', string="Status",
        track_visibility='onchange')

    def action_confirm(self):
        for rec in self:
            name = self.env['ir.sequence'].sudo().next_by_code('asset.depreciation.method.change.request') or 'New'
            rec.write({
                'state': 'confirm',
                'name': name
            })

    def action_approve(self):
        for rec in self:
            rec.write({
                'state': 'approve'
            })

    def action_cancel(self):
        for rec in self:
            rec.write({
                'state': 'approve'
            })
