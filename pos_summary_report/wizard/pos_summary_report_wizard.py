from openerp import api, exceptions, fields, models


class PosSummaryReportWizard(models.TransientModel):
    _name = 'pos.summary.report.wizard'

    @api.model
    def _default_operating_unit(self):
        return self.env.user.default_operating_unit_id.id

    start_date = fields.Date('Start Date', default=fields.Date.today(), required=True)
    end_date = fields.Date('End Date', default=fields.Date.today())
    point_of_sale_id = fields.Many2one('pos.config', string='Point Of Sale',
                                       default=_default_operating_unit, required=True)

    @api.multi
    def pos_order_report(self):

        data = {}
        data['start_date'] = self.start_date
        data['end_date'] = self.end_date
        data['point_of_sale_id'] = self.point_of_sale_id.id
        return self.env['report'].get_action(self, 'pos_summary_report.report_pos_summary_qweb', data=data)
