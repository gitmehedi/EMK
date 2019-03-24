from odoo import api, fields, models,_
import time

class LCStatusWizard(models.TransientModel):
    _name = 'lc.status.wizard'

    status = fields.Selection([
        ('active', 'Active'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], string="Status", required=True)
    month = fields.Selection([
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ], string="Month")
    year = fields.Selection([
        ('1', '2019'),
        ('2', '2020'),
        ('3', '2021'),
        ('4', '2022'),
        ('5', '2023'),
        ('6', '2024'),
        ('7', '2025'),
        ('8', '2026'),
        ('9', '2027'),
        ('10', '2028'),
        ('11', '2029'),
        ('12', '2030'),
    ], string="Year")
    product_id = fields.Many2one('product.template', string='Product')

    @api.multi
    def process_print(self):
        data = {}
        data['month'] = self.month
        data['year'] = self.year
        data['product_id'] = self.product_id.name
        data['status'] = self.status

        return self.env['report'].get_action(self, 'lc_sales_product_foreign.lc_status_foreign_template', data=data)
