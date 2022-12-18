from odoo import api, exceptions, fields, models, _


class LandedCostReportWizard(models.TransientModel):
    _name = 'landed.cost.report.wizard'

    landed_cost_id = fields.Many2one('purchase.cost.distribution', string='Landed cost',
                                     default=lambda self: self.env.context.get('active_id'))

    @api.model
    def _get_product(self):
        if not self.env.context.get('active_id'):
            return [('id', '=', -1)]
        else:
            product_list = []
            landed_cost = self.env['purchase.cost.distribution'].browse(self.env.context.get('active_id'))
            for cost_line in landed_cost.cost_lines:
                product_list.append(cost_line.product_id.id)
            if product_list:
                product_list = list(set(product_list))
                domain = [('id', 'in', product_list)]
                return domain
            return [('id', '=', -1)]

    product_id = fields.Many2one('product.product', domain=_get_product)

    @api.multi
    def print_landed_cost_xls(self):
        return self.env['report'].get_action(self, report_name='purchase_landed_cost_extend.landed_cost_report_xlsx')

