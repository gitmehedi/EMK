from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning


class AccountTPMConfig(models.Model):
    _name = 'account.app.config'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'TPM Management'
    _rec_name = 'config_type'
    _order = 'id desc'

    journal_id = fields.Many2one('account.journal', string='TPM Journal', required=True, track_visibility='onchange')
    tpm_general_account_id = fields.Many2one('account.account', string='General Account', required=True,
                                             track_visibility='onchange', domain="[('level_id.name','=','Layer 5')]")
    tpm_income_account_id = fields.Many2one('account.account', string='Income Account', required=True,
                                            track_visibility='onchange', domain="[('level_id.name','=','Layer 5')]")
    tpm_income_seq_id = fields.Many2one('sub.operating.unit', string='Income Account Sequence', required=True,
                                        track_visibility='onchange')
    tpm_expense_account_id = fields.Many2one('account.account', string='Expense Account', required=True,
                                             track_visibility='onchange', domain="[('level_id.name','=','Layer 5')]")
    tpm_expense_seq_id = fields.Many2one('sub.operating.unit', string='Expense Account Sequence', required=True,
                                         track_visibility='onchange')

    impact_count = fields.Integer(string='Expense Journal', default=1, required=True)
    impact_unit = fields.Selection([('days', 'Days'), ('month', 'Month')], default='days', required=True)
    income_rate = fields.Float(string='Income Rate', required=True, track_visibility='onchange')
    expense_rate = fields.Float(string='Expense Rate', required=True, track_visibility='onchange')
    days_in_fy = fields.Integer(string='Days in Year', size=3, required=True, default=360, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft')], track_visibility='onchange')
    config_type = fields.Selection([('tpm', 'TPM Configuration')], default='tpm', required=True,
                                   track_visibility='onchange', readonly=True)
    excl_br_ids = fields.Many2many('operating.unit', 'tpm_branch_rel', 'tpm_id', 'branch_id',
                                   track_visibility='onchange', string='Exclude Branch')

    @api.constrains('config_type')
    def _check_unique_constrain(self):
        if self.config_type:
            name = self.search([('config_type', '=', self.config_type)])
            if len(name) > 1:
                raise Warning('[Unique Error] Can\'t  create same configuration name multiple times!')
