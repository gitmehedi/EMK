from datetime import datetime
from openerp import api, models, fields
from openerp.exceptions import ValidationError


class ProductUsageHistoryModel(models.Model):
    _name = 'product.usage.history'
    _description = 'Model stores all kinds of product usage data.'
    _rec_name = 'product_id'

    @api.multi
    @api.constrains('product_id', 'period_id', 'operating_unit_id')
    def _check_duplicate(self):
        ex_prod_req = self.search([('operating_unit_id','=',self.operating_unit_id.id),
                                   ('product_id', '=', self.product_id.id),
                                   ('period_id', '=', self.period_id.id)])
        if len(ex_prod_req)>1:
                raise ValidationError(
                    ('This is a duplicate record.'))

    @api.model
    def get_current_period(self):
        time = datetime.now()
        next_month = "{0}-{1}-01".format(time.year, time.month, time.day)
        next_period = self.env['account.period'].search(
            [('date_start', '=', next_month), ('special', '=', False), ('state', '=', 'draft')], order='id ASC',
            limit=1)

        return next_period

    @api.model
    def _default_operating_unit(self):
        return self.env.user.default_operating_unit_id

    value = fields.Float(string='Value', required=True)

    """ Relational Filds """
    product_id = fields.Many2one('product.product', string='Product', required=True)
    period_id = fields.Many2one('account.period', string='Period', required=True,
                                domain="[('special','=',False),('state','=','draft')]", default=get_current_period)
    uom_id = fields.Many2one(related='product_id.uom_id', string='Unit of Measurement', readonly=True, store=True)
    category_id = fields.Many2one(related='product_id.product_tmpl_id', string='Product Category', readonly=True, store=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Branch', required=True,
                                        default=_default_operating_unit,
                                        domain=[('active','=',True)])

    @api.one
    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id

    @api.one
    def name_get(self):
        name = self.product_id
        if self.operating_unit_id and self.period_id and self.product_id:
            name = '%s - %s - %s' % (self.operating_unit_id.name, self.period_id.name, self.product_id.display_name)
        return (self.id, name)

