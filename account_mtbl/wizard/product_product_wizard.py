from odoo import models, fields, api, _
from odoo.exceptions import Warning


class ProductProductWizard(models.TransientModel):
    _name = 'product.product.wizard'

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
    standard_price = fields.Float('Cost Price')
    account_tds_id = fields.Many2one('tds.rule', string='TDS Rule')
    supplier_taxes_id = fields.Many2many('account.tax', 'product_wiz_supplier_taxes_rel', 'prod_id', 'tax_id',
                                         string='Vendor Taxes',
                                         domain=[('type_tax_use', '=', 'purchase')])
    default_code = fields.Char('Internal Reference', index=True)
    type = fields.Selection([('consu', 'Product'), ('service', 'Service'), ('asset', 'Assets')], string='Product Type')
    asset_category_id = fields.Many2one('account.asset.category', string='Asset Type')
    asset_type_id = fields.Many2one('account.asset.category', string='Asset Category')
    property_account_expense_id = fields.Many2one('account.account', string="Expense Account")
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Sequence')

    @api.onchange('asset_category_id')
    def onchange_asset_category(self):
        res = {}
        self.asset_type_id=None
        category_ids = self.env['account.asset.category'].search([('parent_id', '=', self.asset_category_id.id)])
        res['domain'] = {
            'asset_type_id': [('id', 'in', category_ids.ids)],
        }
        return res

    @api.onchange('property_account_expense_id')
    def _onchange_property_account_expense_id(self):
        for rec in self:
            rec.sub_operating_unit_id = None

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.env['product.product'].search(
                [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                 ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.multi
    def act_change_name(self):
        id = self._context['active_id']

        name = self.env['product.product'].search([('name', '=ilike', self.name)])
        if len(name) > 0:
            raise Warning('[Unique Error] Name must be unique!')

        pending = self.env['history.product.product'].search([('state', '=', 'pending'), ('line_id', '=', id)])
        if len(pending) > 0:
            raise Warning('[Warning] You already have a pending request!')

        self.env['history.product.product'].create({'line_id': id,
                                                    'change_name': self.name, 'status': self.status,
                                                    'standard_price': self.standard_price,
                                                    'account_tds_id': self.account_tds_id.id,
                                                    'supplier_taxes_id': [(6, 0, self.supplier_taxes_id.ids)],
                                                    'default_code': self.default_code,
                                                    'request_date': fields.Datetime.now(),
                                                    'type': self.type,
                                                    'asset_category_id': self.asset_category_id.id if self.asset_category_id else None,
                                                    'asset_type_id': self.asset_type_id.id if self.asset_type_id else None,
                                                    'property_account_expense_id': self.property_account_expense_id.id if self.property_account_expense_id else None,
                                                    'sub_operating_unit_id': self.sub_operating_unit_id.id if self.sub_operating_unit_id else None
                                                    })

        record = self.env['product.product'].search(
            [('id', '=', id), '|', ('active', '=', False), ('active', '=', True)])
        if record:
            record.write({'pending': True, 'maker_id': self.env.user.id})
