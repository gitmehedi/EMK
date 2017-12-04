from openerp import api, exceptions, fields, models


class CategoryWiseProductReportWizard(models.TransientModel):
    _name = 'category.wise.product.report.wizard'

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', default=fields.Date.today(), required=True)
    shop_id = fields.Many2one('operating.unit', string='Shop Name', required=True)
    category_id = fields.Many2one('operating.unit', string='Category')

    # @api.onchange('operating_unit_id')
    # def onchange_operating_unit_id(self):
    #     res = {}
    #     self.point_of_sale_id = 0
    #     if self.operating_unit_id:
    #         lists = self.env['pos.config'].search(
    #             [('operating_unit_id', '=', self.operating_unit_id.id), ('active_shop', '=', True)])
    #         self.point_of_sale_id = lists.id
    #
    #     return res

    @api.multi
    def report_print(self):
        data = {}
        data['start_date'] = self.start_date
        data['end_date'] = self.end_date
        data['shop_id'] = self.shop_id.id
        data['category_id'] = self.category_id.id

        return self.env['report'].get_action(self, 'pos_summary_report.report_category_wise_product_report_qweb',
                                             data=data)
