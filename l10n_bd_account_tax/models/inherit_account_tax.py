from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

VAT_AMOUNT_TYPE = [('group', 'Group of Taxes'), ('fixed', 'Fixed'), ('percent', 'Percentage of Price'),
                   ('division', 'Percentage of Price Tax Included')]
TDS_AMOUNT_TYPE = [('percent', 'Percentage of Price'), ('division', 'Percentage of Price Tax Included'),
                   ('slab', 'Slab')]


class AccountTax(models.Model):
    _name = 'account.tax'
    _inherit = ['account.tax', 'mail.thread']

    def _selection_amount_type(self):
        lst = VAT_AMOUNT_TYPE
        if self._context.get('default_is_tds'):
            lst = TDS_AMOUNT_TYPE

        return lst

    name = fields.Char(track_visibility='onchange', string='Name')
    description = fields.Char(track_visibility='onchange')

    amount = fields.Float(track_visibility='onchange')

    type_tax_use = fields.Selection(track_visibility='onchange')
    amount_type = fields.Selection(_selection_amount_type, track_visibility='onchange')

    active = fields.Boolean(track_visibility='onchange')
    is_reverse = fields.Boolean(string='Reverse Accounting', track_visibility='onchange')
    is_vat = fields.Boolean(string='VAT Rule', track_visibility='onchange')
    is_tds = fields.Boolean(string='TDS Rule', track_visibility='onchange')
    price_include = fields.Boolean(track_visibility='onchange')
    include_base_amount = fields.Boolean(track_visibility='onchange')
    tax_adjustment = fields.Boolean(track_visibility='onchange')
    price_exclude = fields.Boolean(string='Excluded in Price', default=False, track_visibility='onchange')
    effect_base_price = fields.Boolean(string='Effect On Base Price', default=False, track_visibility='onchange')

    account_id = fields.Many2one(track_visibility='onchange')
    refund_account_id = fields.Many2one(track_visibility='onchange')
    tax_group_id = fields.Many2one(track_visibility='onchange')
    tag_ids = fields.Many2many(track_visibility='onchange')
    line_ids = fields.One2many('account.tax.line', 'tax_id', string='Slab Lines')

    mushok_amount = fields.Float(string='Mushok Value', digits=(16, 4), default=0.0, track_visibility='onchange',
                                 help='For Mushok-6.3')
    vds_amount = fields.Float(string='VDS Authority Value', digits=(16, 4), default=0.0, track_visibility='onchange',
                              help='For VDS Authority')

    include_in_expense = fields.Boolean(string='Include In Expense', track_visibility='onchange')

    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id, type_tax_use,is_tds)', 'Name must be unique !'),
    ]

    @api.constrains('amount')
    def constrains_amount(self):
        if self.amount < 0:
            raise ValidationError(_("[Validation Error] Amount can not be negative."))

    @api.constrains('mushok_amount')
    def constrains_mushok_amount(self):
        if self.mushok_amount < 0:
            raise ValidationError(_("[Validation Error] Mushok Value can not be negative."))

    @api.constrains('vds_amount')
    def constrains_vds_amount(self):
        if self.vds_amount < 0:
            raise ValidationError(_("[Validation Error] VDS Authority Value can not be negative."))

    @api.onchange('name')
    def onchange_strips(self):
        if self.name:
            self.name = str(self.name.strip()).upper()

    @api.onchange('amount_type')
    def onchange_amount_type(self):
        if self.amount_type == 'slab':
            self.price_include = False
            self.include_base_amount = False

    def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None):
        if self.amount_type == 'slab':
            res = 0.0
        else:
            res = super(AccountTax, self)._compute_amount(base_amount, price_unit, quantity, product, partner)

        return res


class AccountTaxLine(models.Model):
    _name = 'account.tax.line'

    tax_id = fields.Many2one('account.tax')
    range_from = fields.Integer(string='From Range', required=True)
    range_to = fields.Integer(string='To Range', required=True)
    rate = fields.Float(string='Rate', required=True, digits=(13, 2))

    @api.constrains('range_from', 'range_to')
    def _check_time(self):
        for rec in self:
            domain = [
                ('range_from', '<', rec.range_to),
                ('range_to', '>', rec.range_from),
                ('id', '!=', rec.id),
                ('tax_id', '=', rec.tax_id.id)
            ]
            check_domain = self.search_count(domain)
            if check_domain:
                date_time_range_from = str(rec.range_from)
                date_time_range_to = str(rec.range_to)
                raise ValidationError(_(
                    " The Range (%s)  and  (%s)  are overlapping with existing Slab ." % (
                        date_time_range_from, date_time_range_to)
                ))


class AccountTaxSlabLine(models.Model):
    _name = 'account.tax.slab.line'

    invoice_amount = fields.Float(string='Invoice Amount')
    tds_amount = fields.Float(string='TDS Amount')
    date = fields.Date(string='Date')
    partner_id = fields.Many2one('res.partner', required=True, domain=[('supplier', '=', True)])
    tax_id = fields.Many2one('account.tax', required=True, domain=[('is_tds', '=', True)])
    tax_fy_id = fields.Many2one('date.range', required=True, domain=[('type_id.tds_year', '=', True)])
    invoice_id = fields.Many2one('account.invoice')
    advance_id = fields.Many2one('vendor.advance')
    state = fields.Selection(selection=[('demo', 'Demo')], string='State')

    def get_prev_slab_inv(self, partner, tds, date, advance_id=None):
        fy = self.get_fy(date)

        if not advance_id:
            domain = [('partner_id', '=', partner.id),
                      ('tax_id', '=', tds),
                      ('tax_fy_id', '=', fy.id),
                      ('date', '<=', date)]
        else:
            domain = [('partner_id', '=', partner.id),
                      ('tax_id', '=', tds),
                      ('tax_fy_id', '=', fy.id),
                      ('vendor_advance_id', '!=', advance_id),
                      ('date', '<=', date)]

        prev_obj = self.search(domain)
        prev_inv_amount = sum([inv.invoice_amount for inv in prev_obj])
        prev_tds_amount = sum([inv.tds_amount for inv in prev_obj])
        # ('vendor_advance_id', '!=', self.id)
        return {
            'prev_inv_amount': prev_inv_amount,
            'prev_tds_amount': prev_tds_amount
        }

    def create_slab_line(self, lines, inv):
        fy = self.get_fy(inv.date_invoice)
        for key, val in lines.items():
            create = {
                'invoice_amount': val['inv_amount'],
                'tds_amount': inv.amount_tds,
                'partner_id': inv.partner_id.id,
                'tax_id': val['tds_id'].id,
                'tax_fy_id': fy.id,
                'date': inv.date_invoice,
                'invoice_id': inv.id,
            }
            self.create(create)

    def get_fy(self, date):
        # The date will not be system date, it will be invoice date
        fy = self.env['date.range'].search(
            [('date_start', '<=', date), ('date_end', '>=', date), ('type_id.tds_year', '=', True),
             ('active', '=', True)], order='id DESC', limit=1)
        if not fy:
            raise ValidationError(_('Please create a TDS year'))
        return fy
