from openerp import api, fields, models


class ProductListWizard(models.TransientModel):
    _name = 'product.list.wizard'

    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date', default=fields.Date.today())

    """ Relational Fields"""
    location_id = fields.Many2one('stock.location', string='Stock Location', required=True)
    category_id = fields.Many2one('product.category', string='Category')
    product_id = fields.Many2one('product.template', string='Product')

    @api.multi
    def print_report(self, data):
        return self.env['report'].get_action(self, 'stock_summary_report.report_stock_summary_qweb', data=data)
