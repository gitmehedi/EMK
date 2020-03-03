from odoo import api, models, fields, _
from odoo import exceptions

class AttendanceSummaryReport(models.AbstractModel):
    _name = "report.gbs_hr_attendance_report.report_att_summ_temp"

    @api.model
    def render_html(self, docids, data=None):
        if len(data['department_id'])==1:
            dept = self.env['hr.department'].search([('id', '=', data['department_id'][0])])
        else:
            dept = self.env['hr.department'].search([('id', 'in', tuple(data['department_id']))])
        dpt_att_summary_list = []
        sn = 1
        ou_ids = '(' + str(data['operating_unit_id'][0]) + ')' if len(data['operating_unit_id']) == 1 else tuple(data['operating_unit_id'])
        for d in dept:
            dpt_att_summary = {}
            dept_id = d.id
            dpt_att_summary['name'] = d.name
            dpt_att_summary['seq'] = d.sequence
            dpt_att_summary['val'] = self.get_data(data, dept_id, ou_ids)

            if dpt_att_summary['val'] is not False:
                for ps in dpt_att_summary['val']:
                    ps['sn'] = sn
                    sn += 1
                emp_sort_list = dpt_att_summary['val']
                emp_sort_list = sorted(emp_sort_list, key=lambda k: k['sn'])
                dpt_att_summary['val'] = emp_sort_list
                dpt_att_summary_list.append(dpt_att_summary)
            else:
                pass

        docargs = {
            'docs': dpt_att_summary_list,
            'data': data,
            'company': data['company_name'],
            'operating_unit': data['ou_name'],
            'docs_len': 20
        }
        return self.env['report'].render('gbs_hr_attendance_report.report_att_summ_temp', docargs)

    def get_data(self, data, dept, ou_ids):

        from_date = "'" + str(data['date_from']) + "'"
        to_date = "'" + str(data['date_to']) + "'"

        self._cr.execute('''
                    SELECT he.id, 
                           he.name_related AS name, 
                           he.employee_sequence AS emp_seq,
                           hj.name AS designation
                    FROM   hr_employee he 
                           LEFT JOIN hr_job hj 
                                  ON ( hj.id = he.job_id ) 
                           LEFT JOIN hr_department hd 
                                  ON ( hd.id = he.department_id )
                           LEFT JOIN operating_unit ou 
                                      ON ( ou.id = he.operating_unit_id )
                    WHERE he.operating_unit_id in %s 
                          AND he.department_id = %s
                          AND he.company_id = %s
                ''' % (ou_ids, dept, data['company_id']))

        query_data = self._cr.fetchall()

        if query_data:
            report_data = {
                    data[0]: {
                    'emp_name': data[1],
                    'designation': data[3],
                    'emp_seq': data[2],
                    'absent_days': 0,
                    'late_days': 0
                    }
                for data in query_data
            }

            absent_day_data = self._get_absent_data(data, dept, from_date, to_date, ou_ids)

            if absent_day_data:
                for record in absent_day_data:
                    report_data[record[0]]['absent_days'] = record[1]

            late_day_data = self._get_late_data(data, dept, from_date, to_date, ou_ids)

            if late_day_data:
                for record in late_day_data:
                    report_data[record[0]]['late_days'] = record[1]

            final_data = [report_data[i] for i in report_data]

            return final_data
        else:
            return False

    def _get_absent_data(self, data, dept, from_date, to_date, ou_ids):
        absent_day_sql = '''
                      SELECT DISTINCT ON(he.id) he.id,
                             COUNT(haad.date) AS absent_days
                      FROM hr_attendance_absent_day haad
                      INNER JOIN hr_attendance_summary_line hasl
                            ON (hasl.id = haad.att_summary_line_id)
                      INNER JOIN hr_employee he
                            ON (he.id = hasl.employee_id)
                      WHERE haad.date BETWEEN %s AND %s
                            AND he.operating_unit_id IN %s
                            AND he.company_id = %s
                            AND he.department_id = %s
                            AND hasl.state = 'approved'
                      GROUP BY he.id,haad.att_summary_line_id
                      ORDER BY he.id
                            ''' % (from_date, to_date, ou_ids, data['company_id'], dept)

        self._cr.execute(absent_day_sql)

        return self._cr.fetchall()

    def _get_late_data(self, data, dept, from_date, to_date,ou_ids):

        late_day_sql = '''
                      SELECT DISTINCT ON(he.id) he.id,
                             COUNT(hald.date) AS late_days
                      FROM hr_attendance_late_day hald
                      INNER JOIN hr_attendance_summary_line hasl
                       ON (hasl.id = hald.att_summary_line_id)
                      INNER JOIN hr_employee he
                       ON (he.id = hasl.employee_id)
                      WHERE hald.date BETWEEN %s AND %s
                            AND he.operating_unit_id IN %s
                            AND he.company_id = %s
                            AND he.department_id = %s
                            AND hasl.state = 'approved'
                      GROUP BY he.id,hald.att_summary_line_id
                      ORDER BY he.id
                            ''' % (from_date, to_date, ou_ids, data['company_id'], dept)
        self._cr.execute(late_day_sql)

        return self._cr.fetchall()








