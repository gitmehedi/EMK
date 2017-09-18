from openerp import api, exceptions, fields, models


class WarehouseToShopDistributionWizard(models.TransientModel):
    _name = 'warehouse.to.shop.distribution.report.wizard'

    @api.model
    def _default_operating_unit(self):
        return self.env.user.default_operating_unit_id.id

    def default_warehouse(self):
        warehouse = self.env['stock.location'].search([('id', '=', '12')])
        return warehouse.id


    start_date = fields.Date('Start Date',  required=True)
    end_date = fields.Date('End Date', default=fields.Date.today(), required=True)
    warehouse_id = fields.Many2one('stock.location', 'Warehouse Name', default=default_warehouse)
    operating_unit_id = fields.Many2one('operating.unit', string='Shop', required=True)
    point_of_sale_id = fields.Many2one('pos.config', string='Point of Sale')

    @api.onchange('operating_unit_id')
    def onchange_operating_unit_id(self):
        res = {}
        self.point_of_sale_id = 0
        if self.operating_unit_id:
            lists = self.env['pos.config'].search(
                [('operating_unit_id', '=', self.operating_unit_id.id), ('active_shop', '=', True)])
            self.point_of_sale_id = lists.id

        return res

    @api.multi
    def pos_order_report(self):
        data = {}
        data['start_date'] = self.start_date
        data['end_date'] = self.end_date
        data['source_location_id'] = self.warehouse_id.id
        data['operating_unit_id'] = self.operating_unit_id.id
        data['destination_location_id'] = self.point_of_sale_id.stock_location_id.id
        return self.env['report'].get_action(self, 'pos_summary_report.report_warehouse_to_shop_distribution_report_view_qweb', data=data)
