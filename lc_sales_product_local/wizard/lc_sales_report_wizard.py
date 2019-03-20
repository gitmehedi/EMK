from odoo import api, fields, models


class LcSalesReportWizard(models.TransientModel):
    _name = 'lc.sales.report.wizard'

    @api.multi
    def process_report(self):
        data = {}
        data['shipment_id'] = self.env.context.get('active_id')
        return self.env['report'].get_action(self, 'lc_sales_product_local.report_top_sheet', data)


    @api.multi
    def process_commercial_invoice(self):

        return self.env['report'].get_action(self, 'lc_sales_product_local.report_commercial_invoice',
                                             {'lc_id':self.env.context.get('active_id')})

    @api.multi
    def process_packing_list(self):
        data = {}
        data['shipment_id'] = self.env.context.get('active_id')
        return self.env['report'].get_action(self, 'lc_sales_product_local.report_packing_list', data)

    @api.multi
    def process_measurement_list(self):
        data = {}
        data['shipment_id'] = self.env.context.get('active_id')
        return self.env['report'].get_action(self, 'lc_sales_product_local.report_measurement_list', data)

    @api.multi
    def process_bill_exchange(self):
        data = {}
        data['shipment_id'] = self.env.context.get('active_id')
        return self.env['report'].get_action(self, 'lc_sales_product_local.report_bill_exchange', data)

    @api.multi
    def process_bill_exchange_second(self):
        data = {}
        data['shipment_id'] = self.env.context.get('active_id')
        return self.env['report'].get_action(self, 'lc_sales_product_local.report_bill_exchange_second', data)

    @api.multi
    def process_beneficiary_certificate(self):
        data = {}
        data['shipment_id'] = self.env.context.get('active_id')
        return self.env['report'].get_action(self, 'lc_sales_product_local.report_beneficiary_certificate', data)

    @api.multi
    def process_inspection_certificate(self):
        data = {}
        data['shipment_id'] = self.env.context.get('active_id')
        return self.env['report'].get_action(self, 'lc_sales_product_local.report_inspection_certificate', data)

    @api.multi
    def process_certificate_origin(self):
        data = {}
        data['shipment_id'] = self.env.context.get('active_id')
        return self.env['report'].get_action(self, 'lc_sales_product_local.report_certificate_origin', data)

    @api.multi
    def process_delivery_challan(self):
        data = {}
        data['shipment_id'] = self.env.context.get('active_id')
        return self.env['report'].get_action(self, 'lc_sales_product_local.report_delivery_challan', data)

    @api.multi
    def process_truck(self):
        data = {}
        data['shipment_id'] = self.env.context.get('active_id')
        return self.env['report'].get_action(self, 'lc_sales_product_local.report_truck_receipt', data)

    @api.multi
    def process_party_receiving(self):
        data = {}
        data['shipment_id'] = self.env.context.get('active_id')
        return self.env['report'].get_action(self, 'lc_sales_product_local.report_party_receiving', data)
