from odoo import api, fields, models
import time, datetime


class PartnerSelectionWizard(models.Model):
    _name = 'partner.selection.report.wizard'

    #partner_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)])

    date = fields.Date(string='Date', required=True)

    @api.multi
    def send_date_val(self):

        return self.env['report'].get_action(self, 'delivery_jar_counting.report_jar_summary',
                                          data={'date':self.date})
