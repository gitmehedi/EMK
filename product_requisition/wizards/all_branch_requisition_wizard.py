from datetime import datetime

from openerp import api, fields, models


class ProductUsageSummaryWizard(models.TransientModel):
    _name = 'all.branch.requisition.wizard'

    @api.model
    def get_current_period(self):
        time = fields.Datetime.now()
        next_month = "{0}-{1}-01".format(time.year, time.month, time.day)
        next_period = self.env['account.period'].search(
            [('date_start', '>=', next_month), ('special', '=', False), ('state', '=', 'draft')], order='id ASC',
            limit=1)

        return next_period

    period_id = fields.Many2one('account.period', string='For The Period Of', required=True,
                                domain="[('special','=',False),('state','=','draft')]", default=get_current_period)

    @api.multi
    def print_report(self, data):
        data = {}
        data['start_date'] = self.period_id.name
        data['end_date'] = self.period_id.name
        data['period_name'] = self.period_id.name
        data['period_id'] = self.period_id.id

        return self.env['report'].get_action(self,
                                             'product_requisition.report_all_branch_requisition_report_view_qweb',
                                             data=data)
