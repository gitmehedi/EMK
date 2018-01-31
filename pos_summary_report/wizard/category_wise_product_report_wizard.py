from openerp import api, exceptions, fields, models


class CategoryWiseProductReportWizard(models.TransientModel):
    _name = 'category.wise.product.report.wizard'

    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date', default=fields.Date.today())
    shop_id = fields.Many2one('operating.unit', string='Shop Name', required=True)
    category_id = fields.Many2one('operating.unit', string='Category')

    @api.multi
    def report_print(self):
        data = {}
        data['shop_id'] = self.shop_id.id
        data['category_id'] = self.category_id.id

        return self.env['report'].get_action(self, 'pos_summary_report.report_category_wise_product_report_qweb',
                                             data=data)
