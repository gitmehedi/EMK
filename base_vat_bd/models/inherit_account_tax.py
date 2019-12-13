from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountTax(models.Model):
    _name = 'account.tax'
    _order = 'name desc'
    _inherit = ['account.tax', 'mail.thread']

    mushok_amount = fields.Float(string='Mushok Value',track_visibility='onchange',
                                 readonly=True, states={'draft': [('readonly', False)]}, help='For Mushok-6.3')
    vds_amount = fields.Float(string='VDS Authority Value', track_visibility='onchange',
                              readonly=True, states={'draft': [('readonly', False)]}, help='For VDS Authority ')
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirmed"),
    ], default='draft', string="Status", track_visibility='onchange')

    @api.constrains('mushok_amount', 'vds_amount')
    def _check_mushok_vds_amount(self):
        if self.mushok_amount and self.amount and self.mushok_amount > self.amount:
            raise Warning('Mushok Amount should be less then Rate Amount!')
        if self.vds_amount and self.amount and self.vds_amount >= self.amount:
            raise Warning('VDS Amount should be less then Rate Amount!')

    @api.multi
    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You can not delete a record which is not in draft state!'))
        return super(AccountTax, self).unlink()
