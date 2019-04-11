from odoo import api, fields, models,_


class BillExchangeWizard(models.TransientModel):
    _name = 'bill.of.exc.wizard'

    bill_exchange = fields.Selection([
        ('first', 'First'),
        ('second', 'Second'),
        ('single', 'Single'),
    ], string="Bill of Exchange No.", required=True)

    @api.multi
    def process_bill_exchange(self):
        data = {}
        data['shipment_id'] = self.env.context.get('shipment_id')
        data['bill_exchange'] = self.bill_exchange
        return self.env['report'].get_action(self, 'lc_sales_product_foreign.report_bill_exchange', data)

class BeneficiaryCertificate(models.TransientModel):
    _name = 'beneficiary.certificate.wizard'

    lc_clause = fields.Char(string='LC Clause', default='(AS PER LC CLAUSE 46A: POINT 3)')

    @api.multi
    def process_beneficiary_certificate(self):
        data = {}
        data['shipment_id'] = self.env.context.get('shipment_id')
        data['lc_clause'] = self.lc_clause
        return self.env['report'].get_action(self, 'lc_sales_product_foreign.report_beneficiary_certificate', data)


class LcSalesReportWizard(models.TransientModel):
    _name = 'lc.sales.report.foreign.wizard'


    @api.multi
    def process_packing_list(self):
        data = {}
        data['shipment_id'] = self.env.context.get('active_id')
        return self.env['report'].get_action(self, 'lc_sales_product_foreign.report_packing_list', data)

    @api.multi
    def process_commercial_invoice(self):
        return self.env['report'].get_action(self, 'lc_sales_product_foreign.report_commercial_invoice',
                                             {'lc_id': self.env.context.get('active_id')})

    @api.multi
    def process_certificate_origin(self):
        data = {}
        data['shipment_id'] = self.env.context.get('active_id')
        return self.env['report'].get_action(self, 'lc_sales_product_foreign.report_certificate_origin', data)

    @api.multi
    def process_ls_status_summary(self):
        data = {}
        data['shipment_id'] = self.env.context.get('active_id')
        return self.env['report'].get_action(self, 'lc_sales_product_foreign.lc_status_foreign_template', data)

    @api.multi
    def action_ls_status_summary(self):
        res = self.env.ref('lc_sales_product_foreign.lc_status_wizard_view')
        result = {
            'name': _('LC Status'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'lc.status.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {'shipment_id': self.env.context.get('active_id')},
        }
        return result

    @api.multi
    def action_bill_of_exchange_no(self):
        res = self.env.ref('lc_sales_product_foreign.bill_of_exc_wizard_view')
        result = {
            'name': _('Bill Exchange Number'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'bill.of.exc.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {'shipment_id': self.env.context.get('active_id')},
        }
        return result

    @api.multi
    def action_beneficiary_certificate(self):
        res = self.env.ref('lc_sales_product_foreign.beneficiary_certificate_wizard_view')
        result = {
            'name': _('Beneficiary Certificate LC Clause'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'beneficiary.certificate.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {'shipment_id': self.env.context.get('active_id')},
        }
        return result