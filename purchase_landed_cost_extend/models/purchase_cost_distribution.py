# import of python
import datetime

# import of odoo
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import frozendict


class PurchaseCostDistribution(models.Model):
    _inherit = 'purchase.cost.distribution'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True, readonly=True,
                                        states={'draft': [('readonly', False)]},
                                        default=lambda self: self.env.user.default_operating_unit_id)
    field_readonly = fields.Boolean(string='Field Readonly')

    @api.multi
    def action_calculate(self):
        # validation
        if any(datetime.datetime.strptime(line.picking_id.date_done, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d") > self.date for line in self.cost_lines):
            raise ValidationError(_("Date cannot be less than the date of transfer of incoming shipments."))

        return super(PurchaseCostDistribution, self).action_calculate()

    @api.multi
    def action_done(self):
        context = dict(self.env.context)
        context.update({
            'datetime_of_price_history': self.date + ' ' + datetime.datetime.now().strftime("%H:%M:%S"),
            'operating_unit_id': self.cost_lines[0].picking_id.operating_unit_id.id
        })
        self.env.context = frozendict(context)

        super(PurchaseCostDistribution, self).action_done()

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            operating_unit = self.env['operating.unit'].browse(vals.get('operating_unit_id'))
            vals['name'] = self.env['ir.sequence'].next_by_code_new('purchase.cost.distribution', self.date, operating_unit)
        if not vals.get('field_readonly', False):
            vals['field_readonly'] = True

        return super(PurchaseCostDistribution, self).create(vals)

    @api.constrains('date')
    def _check_date(self):
        if self.date > datetime.datetime.today().strftime("%Y-%m-%d"):
            raise ValidationError(_("Date cannot be greater than Current Date."))


class PurchaseCostDistributionLine(models.Model):
    _inherit = 'purchase.cost.distribution.line'

    date_done = fields.Datetime(string='Date of Transfer', related='move_id.picking_id.date_done')
