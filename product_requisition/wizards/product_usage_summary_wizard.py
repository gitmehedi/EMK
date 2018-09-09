from datetime import datetime
from openerp import api, fields, models


class ProductUsageSummaryWizard(models.TransientModel):
    _name = 'product.usage.summary.wizard'

    @api.model
    def _default_operating_unit(self):
        if self.env.user.default_operating_unit_id.active==True:
            return self.env.user.default_operating_unit_id

    @api.model
    def get_current_period(self):
        time = fields.Datetime.now()
        next_month = "{0}-{1}-01".format(time.year, time.month, time.day)
        next_period = self.env['account.period'].search(
            [('date_start', '>=', next_month), ('special', '=', False), ('state', '=', 'draft')], order='id ASC',
            limit=1)
        return next_month

    operating_unit_id = fields.Many2one('operating.unit', string='Branch', required=True,
                                        default=_default_operating_unit)

    start_period_id = fields.Many2one('account.period', string='From Period', required=True,
                                      domain="[('special','=',False),('state','=','draft')]",
                                      default=get_current_period)
    end_period_id = fields.Many2one('account.period', string='To Period', required=True,
                                    domain="[('special','=',False),('state','=','draft')]")

    @api.multi
    def print_report(self, data):
        data = {}
        data['start_date'] = self.start_period_id.date_start
        data['start_period_name'] = self.start_period_id.name
        data['start_period_id'] = self.start_period_id.id
        data['end_date'] = self.end_period_id.date_stop
        data['end_period_name'] = self.end_period_id.name
        data['end_period_id'] = self.end_period_id.id
        data['operating_unit_id'] = self.operating_unit_id.id
        data['operating_unit_name'] = self.operating_unit_id.name

        return self.env['report'].get_action(self,
                                             'product_requisition.report_product_usage_summary_report_view_qweb',
                                             data=data)
