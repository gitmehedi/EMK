from odoo import api, fields, models
import time

from datetime import date, datetime


class JarSummaryReportByDate(models.AbstractModel):
    _name = 'report.delivery_jar_counting.report_jar_summary'

    sql = """
        SELECT t1.date,t1.partner_id, t1.jar_type, t1.qty1, t2.qty2,customer.name FROM 
        (SELECT date,partner_id, jar_type, sum(jar_count) AS qty1 FROM delivery_jar_count
        GROUP BY partner_id, jar_type, date) t1
        LEFT JOIN res_partner customer ON customer.id = t1.partner_id
        LEFT JOIN 
        (SELECT partner_id, jar_type, sum(jar_received) AS qty2 FROM jar_received
        GROUP BY partner_id, jar_type) t2
        ON t1.partner_id = t2.partner_id AND t1.jar_type = t2.jar_type
        WHERE t1.date = %s
    """

    @api.model
    def render_html(self, docids, data=None):
        data_list = []
        ReportUtility = self.env['report.utility']

        date_given = data['date']
        self._cr.execute(self.sql, (date_given,))  # Never remove the comma after the parameter
        results = self._cr.fetchall()

        for line in results:
            jar_dict = dict()
            jar_dict['date'] = line[0]
            jar_dict['qty1'] = line[1]
            jar_dict['jar_type'] = line[2]
            jar_dict['qty2'] = line[3]
            jar_dict['name'] = line[5]

            data_list.append(jar_dict)

        docargs = {
            'data_list': data_list,
            'date': ReportUtility.get_date_from_string(data['date']),
        }

        return self.env['report'].render('delivery_jar_counting.report_jar_summary', docargs)
