# -*- coding: utf-8 -*-
##############################################################################
from openerp import api, models
import datetime


class DailyCreditSettlementReport(models.AbstractModel):
    _name = 'report.pos_summary_report.report_pos_summary_qweb'

    def _generate_categories(self, category, categories):
        categories.append(category.id)
        for cat in category.child_id:
            categories = self._generate_categories(cat, categories)
        return categories

    def _generate_lines(self, start_date, end_date, pos_config):

        query = """
                SELECT * FROM pos_order po 
                    INNER JOIN stock_location sl
                    ON (po.location_id = sl.id )
                    INNER JOIN pos_config pc
                    ON (pc.stock_location_id = sl.id )
                    WHERE pc.id = %s and date_order between %s and %s 
                    ORDER BY po.date_order;
        """
        params = (pos_config, start_date, end_date)
        self.env.cr.execute(query, params)
        res =  self.env.cr.dictfetchall()
        return res

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('stock_summary_report.report_stock_summary_qweb')

        lines = self._generate_lines(data['start_date'], data['end_date'], data['point_of_sale_id'])

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'start_date': data['start_date'],
            'end_date': data['end_date'],
            'category_id': data['point_of_sale_id'],
            'lines': lines,
        }
        return report_obj.render('pos_summary_report.report_pos_summary_qweb', docargs)
