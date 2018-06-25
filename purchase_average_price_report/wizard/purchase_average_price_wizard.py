# -*- coding: utf-8 -*-
from odoo import api, fields, models , _
from odoo.exceptions import ValidationError


class PurchaseAveragePriceWizard(models.TransientModel):
    _name = 'purchase.average.price.wizard'

    date_from = fields.Date("Date From", required=True)
    date_to = fields.Date("Date To", required=True)

    @api.constrains('date_from', 'date_to')
    def _check_date_validation(self):
        if self.date_from > self.date_to:
            raise ValidationError(_("From date must be less then To date."))

    @api.multi
    def process_report(self):

        data = {}
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to

        data['operating_unit_id'] = self.env.user.default_operating_unit_id.id

        return self.env['report'].get_action(self, 'purchase_average_price_report.purchase_price_report_temp',
                                             data=data)
