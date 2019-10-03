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

    status = fields.Boolean(string='Active', default=default_status)
    name = fields.Char(string='Requested Name')
    method_progress_factor = fields.Float(string='Depreciation Factor', default=0.0, )
    journal_id = fields.Many2one('account.journal', string='Journal')
    depreciation_year = fields.Integer(string='Asset Life (In Year)', default=0)
    method_number = fields.Integer(string='Number of Depreciations', default=0)
    method = fields.Selection([('degressive', 'Reducing Method'), ('linear', 'Straight Line/Linear')],
                              string='Computation Method', default='degressive')
    account_asset_id = fields.Many2one('account.account', string='Asset Account',
                                       domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)])
    asset_suspense_account_id = fields.Many2one('account.account', string='Asset Awaiting Allocation',
                                                domain=[('deprecated', '=', False)])
    account_depreciation_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)],
                                              string='Accumulated Depreciation A/C', )
    account_depreciation_expense_id = fields.Many2one('account.account', string='Depreciation Exp. A/C',
                                                      domain=[('internal_type', '=', 'other'),
                                                              ('deprecated', '=', False)])
    account_asset_loss_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)],
                                            string='Asset Loss A/C')
    account_asset_gain_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)],
                                            string='Asset Gain A/C')
    asset_sale_suspense_account_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)],
                                                     string='Asset Awaiting Disposal')
    no_depreciation = fields.Boolean(string="No Depreciation", default=False)

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
        no_depreciation = self.no_depreciation if self.no_depreciation else None

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
             'method_progress_factor': method_progress_factor,
             'status': self.status,
             'no_depreciation': self.no_depreciation
             })

        record = self.env['account.asset.category'].search(
            [('id', '=', id), ('state', '!=', 'reject'), '|', ('active', '=', False), ('active', '=', True)])
        if record:
            record.write({'pending': True})
