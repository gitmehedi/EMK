from odoo import api, fields, models, _, SUPERUSER_ID
from psycopg2 import IntegrityError
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    parent_id = fields.Many2one(track_visibility='onchange')
    default_code = fields.Char(track_visibility='onchange')
    barcode = fields.Char(track_visibility='onchange')
    lst_price = fields.Float(track_visibility='onchange')
    standard_price = fields.Float(track_visibility='onchange')

    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange', readonly=True,
                             states={'draft': [('readonly', False)]})
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange')
    line_ids = fields.One2many('history.product.product', 'line_id', string='Lines', readonly=True,
                               states={'draft': [('readonly', False)]})
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Sequence', required=True)

    @api.onchange('property_account_expense_id')
    def onchange_property_account_expense_id(self):
        for rec in self:
            rec.sub_operating_unit_id = None

    @api.one
    def act_draft(self):
        if self.state == 'reject':
            self.write({
                'state': 'draft',
                'pending': True,
                'active': False,
            })

    @api.one
    def act_approve(self):
        if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
            raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
        if self.state == 'draft':
            self.write({
                'state': 'approve',
                'pending': False,
                'active': True,
                'approver_id': self.env.user.id,
            })

    @api.one
    def act_reject(self):
        if self.state == 'draft':
            self.write({
                'state': 'reject',
                'pending': False,
                'active': False,
            })

    @api.one
    def act_approve_pending(self):
        if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
            raise ValidationError(_("[Validation Error] Editor and Approver can't be same person!"))
        if self.pending == True:
            requested = self.line_ids.search([('state', '=', 'pending'), ('line_id', '=', self.id)], order='id desc',
                                             limit=1)
            if requested:
                if requested.change_name:
                    self.name = requested.change_name
                if requested.status:
                    self.active = requested.status
                if requested.standard_price:
                    self.standard_price = requested.standard_price
                if requested.account_tds_id:
                    self.account_tds_id = requested.account_tds_id.id
                if requested.supplier_taxes_id:
                    self.supplier_taxes_id = [(6, 0, requested.supplier_taxes_id.ids)]
                if requested.default_code:
                    self.default_code = requested.default_code
                if requested.type == 'asset':
                    self.type = requested.type
                    self.asset_category_id = requested.asset_category_id.id
                    self.asset_type_id = requested.asset_type_id.id
                else:
                    self.type = requested.type if requested.type else self.type

                if requested.property_account_expense_id and requested.sub_operating_unit_id:
                    self.property_account_expense_id = requested.property_account_expense_id
                    self.sub_operating_unit_id = requested.sub_operating_unit_id

                self.pending = False
                self.approver_id = self.env.user.id
                requested.state = 'approve'
                requested.change_date = fields.Datetime.now()

    @api.one
    def act_reject_pending(self):
        if self.pending == True:
            requested = self.line_ids.search([('state', '=', 'pending'), ('line_id', '=', self.id)], order='id desc',
                                             limit=1)
            if requested:
                self.pending = False
                requested.state = 'reject'
                requested.change_date = fields.Datetime.now()

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.search(
                [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                 ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.onchange("name", "code")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()
        if self.code:
            self.code = str(self.code.strip()).upper()

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'reject'):
                raise ValidationError(_('[Warning] Approves and Rejected record cannot be deleted.'))

            try:
                return super(ProductProduct, rec).unlink()
            except IntegrityError:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while other records still reference it"))


class HistoryProductProduct(models.Model):
    _name = 'history.product.product'
    _description = 'History Product'
    _order = 'id desc'

    change_name = fields.Char('Proposed Name', size=200, readonly=True, states={'draft': [('readonly', False)]})
    status = fields.Boolean('Active', default=True, track_visibility='onchange')
    request_date = fields.Datetime(string='Requested Date')
    change_date = fields.Datetime(string='Approved Date')
    standard_price = fields.Float('Cost Price')
    account_tds_id = fields.Many2one('tds.rule', string='TDS Rule')
    supplier_taxes_id = fields.Many2many('account.tax', string='VAT', domain=[('type_tax_use', '=', 'purchase')])
    default_code = fields.Char('Internal Reference')
    type = fields.Selection([('consu', 'Product'), ('service', 'Service'), ('asset', 'Assets')], string='Product Type')
    asset_type_id = fields.Many2one('account.asset.category', string='Asset Type')
    asset_category_id = fields.Many2one('account.asset.category', string='Asset Category')
    line_id = fields.Many2one('product.product', ondelete='restrict')
    state = fields.Selection([('pending', 'Pending'), ('approve', 'Approved'), ('reject', 'Rejected')],
                             default='pending', string='Status')
    property_account_expense_id = fields.Many2one('account.account', string="Expense Account")
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Sequence')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    property_account_expense_id = fields.Many2one(track_visibility='onchange', required=True)

    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange', readonly=True,
                             states={'draft': [('readonly', False)]})
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange')
    line_ids = fields.One2many('history.product.product', 'line_id', string='Lines', readonly=True,
                               states={'draft': [('readonly', False)]})
    supplier_taxes_id = fields.Many2many(track_visibility='onchange')

    @api.one
    def act_draft(self):
        if self.state == 'reject':
            self.write({
                'state': 'draft',
                'pending': True,
                'active': False,
            })

    @api.one
    def act_approve(self):
        if self.state == 'draft':
            self.write({
                'state': 'approve',
                'pending': False,
                'active': True,
                'approver_id': self.env.user.id,
            })

    @api.one
    def act_reject(self):
        if self.state == 'draft':
            self.write({
                'state': 'reject',
                'pending': False,
                'active': False,
            })

    @api.one
    def act_approve_pending(self):
        if self.pending == True:
            requested = self.line_ids.search([('state', '=', 'pending'), ('line_id', '=', self.id)], order='id desc',
                                             limit=1)
            if requested:
                self.name = self.name if not requested.change_name else requested.change_name
                self.active = requested.status
                self.pending = False
                requested.state = 'approve'
                requested.change_date = fields.Datetime.now()

    @api.one
    def act_reject_pending(self):
        if self.pending == True:
            requested = self.line_ids.search([('state', '=', 'pending'), ('line_id', '=', self.id)], order='id desc',
                                             limit=1)
            if requested:
                self.pending = False
                requested.state = 'reject'
                requested.change_date = fields.Datetime.now()

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'reject'):
                raise ValidationError(_('[Warning] Approves and Rejected record cannot be deleted.'))

            try:
                return super(ProductTemplate, rec).unlink()
            except IntegrityError:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while other records still reference it"))

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.search(
                [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                 ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.onchange("name", "code")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()

    @api.constrains('supplier_taxes_id')
    def _check_supplier_taxes_id(self):
        if self.supplier_taxes_id and len(self.supplier_taxes_id) > 1:
            raise Warning('You can select one VAT!')
