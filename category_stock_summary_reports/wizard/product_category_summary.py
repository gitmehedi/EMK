from openerp import api, exceptions, fields, models


class ProductCategorySummaryWizard(models.TransientModel):
    _name = 'product.category.summary.wizard'

    category_id = fields.Many2one('product.category', string='Category', required=True)
    location_id = fields.Many2one('stock.location', string='Location', domain="[('usage','=','internal')]",
                                  required=True)

    @api.multi
    def report_print(self):
        data = {}
        data['category_name'] = self.category_id.name
        data['category_id'] = self.category_id.id
        data['location_name'] = self.location_id.name
        data['location_id'] = self.location_id.id

        return self.env['report'].get_action(self,
                                             'category_stock_summary_reports.report_product_category_summary_qweb',
                                             data=data)
