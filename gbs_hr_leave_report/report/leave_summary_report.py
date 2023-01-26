from odoo import api, fields, models, _


class HrLeaveSummaryReport(models.AbstractModel):
    _name = 'report.gbs_hr_leave_report.report_emp_leave_summary'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        if data['operating_unit_id']:
            header = {}
            header[0] = 'SI'
            header[1] = 'Name'
            header[2] = 'Employee ID'
            header[3] = 'Designation'
            header[4] = 'Department'
            header_data = self.env['hr.holidays.status'].search([], order='id ASC')
            for val in header_data:
                header[len(header)] = {val.name: {'Avail': 0, 'Balance': 0}}

        lists = self.get_data(data, header_data)

        docargs = {
            'data': data,
            'holiday_objs': lists,
            'header': header
        }
        return report_obj.render('gbs_hr_leave_report.report_emp_leave_summary', docargs)

    @api.model
    def get_data(self, data, header):
        department = '={0} '.format(data['department_id']) if data['department_id'] else 'IS NOT NULL '.format(
            data['department_id'])

        emp_active_condition = ''
        if not data['include_archived']:
            emp_active_condition = " and rr.active=True"

        self._cr.execute('''
            SELECT he.id, 
            he.name_related AS name, 
            he.device_employee_acc as employee_id,
            hj.name         AS designation, 
            hd.name         AS department
            FROM   hr_employee he 
            LEFT JOIN hr_job hj 
            ON ( hj.id = he.job_id ) 
            LEFT JOIN hr_department hd 
            ON ( hd.id = he.department_id )
            LEFT JOIN operating_unit ou 
            ON ( ou.id = he.operating_unit_id )
            LEFT JOIN resource_resource rr 
            ON (rr.id = he.resource_id)
            WHERE ou.id=%s 
                  AND he.department_id %s %s
        ''' % (data['operating_unit_id'], department, emp_active_condition))

        leaves = {val[0]: {
            'name': val[1],
            'employee_id': val[2],
            'designation': val[3],
            'department': val[4],
            'leave': {v.id: {
                'avail': 0,
                'balance': 0
            } for v in header}} for val in self._cr.fetchall()}

        sql = '''
                SELECT he.id,
                       hhl.type, 
                       hhls.id                    AS holiday_type, 
                       Sum(hhl.number_of_days_temp) AS temp_days,
                       Sum(hhl.number_of_days) AS days 
                FROM   hr_holidays hhl 
                       LEFT JOIN hr_holidays_status hhls 
                              ON ( hhls.id = hhl.holiday_status_id ) 
                       LEFT JOIN hr_employee he 
                              ON ( he.id = hhl.employee_id )
                       LEFT JOIN operating_unit ou 
                              ON ( ou.id = he.operating_unit_id )
                      LEFT JOIN resource_resource rr 
                            ON (rr.id = he.resource_id)
                WHERE  ou.id=%s  
                       AND he.department_id   %s
                       AND hhl.leave_year_id=%s
                       AND hhl.state='validate' %s
                GROUP  BY he.name_related, 
                          he.id, 
                          hhls.id,
                          hhl.type
                ''' % (data['operating_unit_id'], department, data['year_id'], emp_active_condition)

        self._cr.execute(sql)
        for record in self._cr.fetchall():
            rec = leaves[record[0]]['leave'][record[2]]

            rec['balance'] = rec['balance'] + record[4]
            if record[1] == 'remove':
                rec['avail'] = rec['avail'] + abs(record[4])

        return leaves
