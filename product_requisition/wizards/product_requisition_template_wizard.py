from datetime import datetime
from openerp import api, fields, models


class ProductRequistionTemplateWizard(models.TransientModel):
    _name = 'product.requisition.template.wizard'

    @api.model
    def _default_operating_unit(self):
        if self.env.user.default_operating_unit_id.active == True:
            return self.env.user.default_operating_unit_id

    operating_unit_id = fields.Many2one('operating.unit', string='Branch', required=True,
                                        default=_default_operating_unit)

    template_id = fields.Many2one('product.requisition.template', string='Select a Template', required=True,
                                  domain="[('status','=',True)]", order="category_id ASC,product_id ASC")

    @api.multi
    def print_report(self, context=None):
        prq = self.env['product.requisition'].browse(context['active_id'])
        prq.line_ids.unlink()

        for rec in self.template_id.line_ids:
            data = {}

            location = self.get_stock_location(prq.operating_unit_id.id)
            quant = self.env['stock.quant'].search([('location_id', '=', location),
                                                    ('product_id', '=', rec.product_id.id)])
            no_of_days = self.last_day_of_month(prq.date, prq.period_id.date_stop)

            stock_in_hand_qty = sum([rec.qty for rec in quant]) if quant else 0
            average_qty = self.average_usage_per_month(rec.product_id, prq)
            required_qty = round(float(average_qty * no_of_days) /30 )
            minimum_stock_quantity = round(float(average_qty * prq.quantity) / 30)

            cal_qty = required_qty + average_qty + minimum_stock_quantity - stock_in_hand_qty

            product_required_qty = cal_qty if cal_qty > 0 else 0
            excess_qty = round(cal_qty, 2) if cal_qty < 0 else 0

            data['product_id'] = rec.product_id.id
            data['uom_id'] = rec.product_id.uom_id.id
            data['stock_in_hand_qty'] = stock_in_hand_qty
            data['required_qty'] = required_qty
            data['average_qty'] = average_qty
            data['minimum_stock_qty'] = minimum_stock_quantity
            data['product_required_qty'] = product_required_qty
            data['excess_qty'] = excess_qty
            data['requisition_id'] = prq.id

            prq.line_ids.create(data)

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'src_model': 'product.requisition',
            'res_model': 'product.requisition',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': prq.id
        }

    def average_usage_per_month(self, product, rec):
        summary = self.env['product.usage.history'].search(
            [('product_id', '=', product.id),
             ('operating_unit_id', '=', rec.operating_unit_id.id),
             ('period_id', '<', rec.period_id.id)],
            order='period_id DESC', limit=12)
        sum, num = 0, 0
        for record in summary:
            if record.value:
                sum = sum + record.value
                num = num + 1
        return round(float(sum) / num) if num != 0 else 10

    @api.model
    def get_stock_location(self, opu_id):
        location = self.env['stock.location'].search(
            [('operating_unit_id', '=', opu_id)])
        return location.id

    def last_day_of_month(self, date, end_date):
        fmt = '%Y-%m-%d'
        date= self.env['account.period'].search([('date_start', '<=', date), ('date_stop', '>=', date)])
        d1 = datetime.strptime(date.date_stop, fmt)
        d2 = datetime.strptime(end_date, fmt)

        return (d2 - d1).days + 1
