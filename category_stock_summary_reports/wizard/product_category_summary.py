from openerp import api, exceptions, fields, models


class ProductCategorySummaryWizard(models.TransientModel):
    _name = 'product.category.summary.wizard'

    category_id = fields.Many2one('product.category', string='Category Name', required=True)
    location_id = fields.Many2one('stock.location', string='Shop Name', domain="[('usage','=','internal')]")

    @api.multi
    def report_print(self):
        data = {}
        data['category_name'] = self.category_id.name
        data['category_id'] = self.category_id.id
        data['location_name'] = self.location_id.name if self.location_id else ''
        data['location_id'] = self.location_id.id if self.location_id else False

        return self.env['report'].get_action(self,
                                             'category_stock_summary_reports.report_product_category_summary_qweb',
                                             data=data)
