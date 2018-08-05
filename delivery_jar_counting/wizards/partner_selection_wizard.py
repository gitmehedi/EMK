from odoo import api, fields, models


class PartnerSelectionWizard(models.Model):
    _name = 'partner.selection.report.wizard'

    partner_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)])


    @api.multi
    def send_partner_id(self):

        return self.env['report'].get_action(self, 'gbs_sales_jar_count.report_jar_summary',
                                          data={'partner_id':self.partner_id.id})
