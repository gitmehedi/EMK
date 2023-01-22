from odoo import models, fields, api, _
from odoo.exceptions import Warning


class AccountAssetCategoryWizard(models.TransientModel):
    _name = 'account.asset.category.wizard'

    @api.model
    def default_name(self):
        context = self._context
        return self.env[context['active_model']].search([('id', '=', context['active_id'])]).name

    @api.model
    def default_status(self):
        context = self._context
        return self.env[context['active_model']].search([('id', '=', context['active_id'])]).active

    @api.model
    def default_method(self):
        context = self._context
        return self.env[context['active_model']].search([('id', '=', context['active_id'])]).method

    status = fields.Boolean(string='Active', default=default_status)
    name = fields.Char(string='Requested Name')
    method_progress_factor = fields.Float(string='Depreciation Factor', digits=(1, 3), default=0.0, )
    journal_id = fields.Many2one('account.journal', string='Journal')
    depreciation_year = fields.Integer(string='Asset Life (In Year)', default=0)
    method_number = fields.Integer(string='Number of Depreciations', default=0)
    method = fields.Selection([('degressive', 'Reducing Method'),
                               ('linear', 'Straight Line/Linear'),
                               ('no_depreciation', 'No Depreciation')], default=default_method,
                              string='Computation Method')
    account_asset_id = fields.Many2one('account.account', string='Asset Account',
                                       domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)])
    asset_suspense_account_id = fields.Many2one('account.account', string='Asset Awaiting Allocation',
                                                domain=[('deprecated', '=', False)])
    account_depreciation_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)],
                                              string='Accumulated Depreciation A/C', required=False)
    account_depreciation_expense_id = fields.Many2one('account.account', string='Depreciation Exp. A/C',
                                                      domain=[('internal_type', '=', 'other'),
                                                              ('deprecated', '=', False)], required=False)
    account_asset_loss_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)],
                                            string='Asset Loss A/C')
    account_asset_gain_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)],
                                            string='Asset Gain A/C')
    asset_sale_suspense_account_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)],
                                                     string='Asset Awaiting Disposal')
    account_asset_seq_id = fields.Many2one('sub.operating.unit', string='Asset Account Sequence')
    asset_suspense_seq_id = fields.Many2one('sub.operating.unit', string='Asset Awaiting Allocation Sequence')
    account_depreciation_seq_id = fields.Many2one('sub.operating.unit', string='Accumulated Depreciation A/C Sequence')
    account_depreciation_expense_seq_id = fields.Many2one('sub.operating.unit', string='Depreciation Exp. A/C Sequence')
    account_asset_loss_seq_id = fields.Many2one('sub.operating.unit', string='Asset Loss A/C Sequence')
    account_asset_gain_seq_id = fields.Many2one('sub.operating.unit', string='Asset Gain A/C Sequence')
    asset_sale_suspense_seq_id = fields.Many2one('sub.operating.unit', string='Asset Awaiting Disposal Sequence')

    @api.onchange('method')
    def onchange_method(self):
        if self.method == 'no_depreciation':
            self.account_depreciation_expense_id = None
            self.account_depreciation_id = None

    @api.multi
    def act_change_name(self):
        id = self._context['active_id']
        obj = self.env['account.asset.category']
        asset = obj.browse(id)
        condition = [('state', '!=', 'reject'), ('parent_id', '!=', None),
                     '|', ('active', '=', True), ('active', '=', False)]
        condition[0] = ('name', '=ilike', self.name.strip()) if self.name else ('name', '=ilike', None)
        if asset.parent_id:
            condition[1] = ('parent_id', '!=', None)
            name = obj.search(condition)
        elif not asset.parent_id:
            condition[1] = ('parent_id', '=', None)
            name = obj.search(condition)

        if len(name) > 0:
            raise Warning('[Unique Error] Name must be unique!')

        if asset.method == 'no_depreciation' and self.method != 'no_depreciation' and not self.account_depreciation_id and not self.account_depreciation_expense_id:
            raise Warning(_('Current Assets depreciation method was No Depreciation. Please chose following fields \n'
                            '- Depreciation Exp. A/C\n - Accumulated Depreciation A/C'))

        journal_id = self.journal_id.id if self.journal_id else None
        depreciation_year = self.depreciation_year if self.depreciation_year else None
        method_number = self.method_number if self.method_number else None
        method = self.method if self.method else None
        account_asset_id = self.account_asset_id.id if self.account_asset_id else None
        asset_suspense_account_id = self.asset_suspense_account_id.id if self.asset_suspense_account_id else None
        account_depreciation_id = self.account_depreciation_id.id if self.account_depreciation_id else None
        account_depreciation_expense_id = self.account_depreciation_expense_id.id if self.account_depreciation_expense_id else None
        account_asset_loss_id = self.account_asset_loss_id.id if self.account_asset_loss_id else None
        account_asset_gain_id = self.account_asset_gain_id.id if self.account_asset_gain_id else None
        asset_sale_suspense_account_id = self.asset_sale_suspense_account_id.id if self.asset_sale_suspense_account_id else None
        method_progress_factor = self.method_progress_factor if self.method_progress_factor else None

        account_asset_seq_id = self.account_asset_seq_id.id if self.account_asset_seq_id else None
        asset_suspense_seq_id = self.asset_suspense_seq_id.id if self.asset_suspense_seq_id else None
        account_depreciation_seq_id = self.account_depreciation_seq_id.id if self.account_depreciation_seq_id else None
        account_depreciation_expense_seq_id = self.account_depreciation_expense_seq_id.id if self.account_depreciation_expense_seq_id else None
        account_asset_loss_seq_id = self.account_asset_loss_seq_id.id if self.account_asset_loss_seq_id else None
        account_asset_gain_seq_id = self.account_asset_gain_seq_id.id if self.account_asset_gain_seq_id else None
        asset_sale_suspense_seq_id = self.asset_sale_suspense_seq_id.id if self.asset_sale_suspense_seq_id else None

        pending = self.env['history.account.asset.category'].search([('state', '=', 'pending'), ('line_id', '=', id)])
        if len(pending) > 0:
            raise Warning('[Warning] You already have a pending request!')

        self.env['history.account.asset.category'].create(
            {'change_name': self.name,
             'request_date': fields.Datetime.now(),
             'line_id': id,
             'method_progress_factor': method_progress_factor,
             'journal_id': journal_id,
             'depreciation_year': depreciation_year,
             'method_number': method_number,
             'method': method,
             'account_asset_id': account_asset_id,
             'asset_suspense_account_id': asset_suspense_account_id,
             'account_depreciation_id': account_depreciation_id,
             'account_depreciation_expense_id': account_depreciation_expense_id,
             'account_asset_loss_id': account_asset_loss_id,
             'account_asset_gain_id': account_asset_gain_id,
             'asset_sale_suspense_account_id': asset_sale_suspense_account_id,
             'account_asset_seq_id': account_asset_seq_id,
             'asset_suspense_seq_id': asset_suspense_seq_id,
             'account_depreciation_seq_id': account_depreciation_seq_id,
             'account_depreciation_expense_seq_id': account_depreciation_expense_seq_id,
             'account_asset_loss_seq_id': account_asset_loss_seq_id,
             'account_asset_gain_seq_id': account_asset_gain_seq_id,
             'asset_sale_suspense_seq_id': asset_sale_suspense_seq_id,
             'status': self.status
             })

        record = self.env['account.asset.category'].search(
            [('id', '=', id), ('state', '!=', 'reject'), '|', ('active', '=', False), ('active', '=', True)])
        if record:
            record.write({'pending': True, 'maker_id': self.env.user.id})
