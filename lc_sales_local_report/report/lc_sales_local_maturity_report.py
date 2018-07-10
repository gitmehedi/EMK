from odoo import api, models

class LCSalesMaturityReport(models.AbstractModel):
    _name = 'report.lc_sales_local_report.lc_sales_maturity_temp'

    @api.multi
    def render_html(self, docids, data=None):

        report_utility_pool = self.env['report.utility']
        op_unit_obj = self.env.user.default_operating_unit_id
        data['address'] = report_utility_pool.getAddressByUnit(op_unit_obj)

        docargs = {
            'doc_ids': self._ids,
            'docs': self,
            'record': data,
            'address': data['address'],

        }
        return self.env['report'].render('lc_sales_local_report.lc_sales_maturity_temp', docargs)