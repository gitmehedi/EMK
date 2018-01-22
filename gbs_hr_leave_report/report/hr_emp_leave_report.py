from odoo import api, fields, models, _


class HrEmpLeaveReport(models.AbstractModel):
    _name = 'report.gbs_hr_leave_report.hr_emp_leave_report'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        if data['operating_unit_id']:
            record = self.env['hr.holidays.status'].search([], order='id ASC')
            lists = {rec.id: {'name': rec.name, 'init_bal': 0, 'avail': 0, 'cur_bal': 0, 'detail': {}} for rec in
                     record}

        sql = self.get_query(data)

        self._cr.execute(sql)
        for record in self._cr.fetchall():
            rec = {}
            line = lists[record[7]]
            rec['from_date'] = record[4][:10] if record[4] else record[4]
            rec['to_date'] = record[5][:10] if record[5] else record[5]
            rec['days'] = abs(record[9])
            rec['type'] = record[8]
            if record[6] == 'add':
                line['init_bal'] = line['init_bal'] + record[9] if record[9] else 0
            else:
                if data['from_date'] and data['to_date']:
                    if record[4] >= data['from_date'] and record[5] <= data['to_date']:
                        line['avail'] = line['avail'] + abs(record[9] if record[9] else 0)
                        line['detail'][record[4]] = rec
                else:
                    line['avail'] = line['avail'] + abs(record[9] if record[9] else 0)
                    line['detail'][record[4]] = rec
            line['cur_bal'] = line['init_bal'] - line['avail']

        docargs = {
            'data': data,
            'lists': lists
        }
        return report_obj.render('gbs_hr_leave_report.hr_emp_leave_report', docargs)

    @api.model
    def get_query(self, data):
        department = '={0} '.format(data['department_id']) if data['department_id'] else 'IS NOT NULL '.format(
            data['department_id'])

        sql = '''
                SELECT he.id AS emp_id,
                       he.name_related AS emp_name, 
                       hj.name         AS designation, 
                       hd.name         AS department, 
                       hhl.date_from,
                       hhl.date_to,
                       hhl.type, 
                       hhls.id         AS holiday_type,
                       hhls.name         AS holiday_name,
                       hhl.number_of_days AS days 
                FROM   hr_holidays hhl 
                       LEFT JOIN hr_holidays_status hhls 
                          ON ( hhls.id = hhl.holiday_status_id ) 
                       LEFT JOIN hr_employee he 
                          ON ( he.id = hhl.employee_id )
                       LEFT JOIN hr_job hj 
                          ON ( hj.id = he.job_id ) 
                       LEFT JOIN hr_department hd 
                          ON ( hd.id = he.department_id )
                       LEFT JOIN operating_unit ou 
                          ON ( ou.id = he.operating_unit_id )
                WHERE  ou.id=%s  
                       AND he.id=%s
                       AND he.department_id   %s
                       AND leave_year_id = %s
                       AND hhl.state='validate'
                ''' % (data['operating_unit_id'], data['emp_id'], department, data['year_id'])

        return sql
