from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class ExecutiveSalesWizard(models.TransientModel):
    _name = "executive.sales.wizard"

    type = fields.Selection([
        ('local', 'Local'),
        ('foreign', 'Foreign')
    ], string='Type', default='local')

    area_id = fields.Many2one('res.partner.area', string='Area')
    country_id = fields.Many2one('res.country', string='Country', domain="[('is_sales_country', '=', True)]")

    date_from = fields.Date("Date From", required=True)
    date_to = fields.Date("Date To", required=True)

    @api.onchange('type')
    def _zone(self):
        self.area_id = None
        self.country_id = None

    @api.constrains('date_from', 'date_to')
    def _check_date_validation(self):
        if self.date_from > self.date_to:
            raise ValidationError(_("From date must be less then To date."))
        elif (datetime.strptime(self.date_to, '%Y-%m-%d') - datetime.strptime(self.date_from, '%Y-%m-%d')).days > 365:
            raise ValidationError(_("Maximum date range is one year."))

    @api.multi
    def process_print(self):
        data = dict()
        data['report_type'] = self.type
        data['area_id'] = self.area_id.id
        data['area_name'] = self.area_id.name
        data['country_id'] = self.country_id.id
        data['country_name'] = self.country_id.name
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to

        return self.env['report'].get_action(self, 'samuda_sales_report.report_executive_sales', data=data)
