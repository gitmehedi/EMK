from odoo import api, fields, models,tools
from datetime import date


class HrAttendanceDashboard(models.Model):
    _name = "hr.attendance.dashboard"
    _auto = False
    _order='operating_unit_name'

    operating_unit_name = fields.Char(string= 'Operating Unit')
    present_count = fields.Integer(string="Present")
    absent_count = fields.Integer(string="Absent")
    total_count = fields.Integer(string="Total")
    late_count = fields.Integer(string="Late")
    color = fields.Integer(string='Color Index', default=0)

    # global variables
    current_date = date.today()
    str_current_date = current_date.strftime("%Y-%m-%d")
    str_end_dt = str_current_date + ' 23:59:59'
    str_strt_dt = str_current_date + ' 00:00:00'
    str_check_in = str_current_date + ' 03:15:00'


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'attendance_dashboard')

        query="""
                CREATE OR REPLACE VIEW hr_attendance_dashboard  AS (
                select row_number() OVER () AS id, 
                       count(e.id) as total_count,
                       o.name as operating_unit_name,
                       count(sub_p_t.sub_emp_id) as present_count ,
                       count(sub_l_t.sub_emp_id) as late_count,
                       (count(e.id)-count(sub_p_t.sub_emp_id)) as absent_count,
                       0 as color
                    from hr_employee e
                    left join operating_unit o on e.operating_unit_id=o.id
                    left join (
                    select distinct(e.id) as sub_emp_id,o.name
                    from hr_employee e left join operating_unit o on o.id=e.operating_unit_id
                    left join hr_attendance a on a.employee_id=e.id
                    where check_in between %s and %s
                    ) as sub_p_t on sub_p_t.sub_emp_id=e.id
                    left join (
                    select distinct(e.id) as sub_emp_id,o.name
                    from hr_employee e left join operating_unit o on o.id=e.operating_unit_id
                    left join hr_attendance a on a.employee_id=e.id
                    where check_in between %s
                    and %s and check_in>%s
                    ) as sub_l_t on sub_l_t.sub_emp_id=e.id
                    group by o.name
                )
            """
        self._cr.execute(query, tuple([self.str_strt_dt,self.str_end_dt,self.str_strt_dt,self.str_end_dt,self.str_check_in]))

    @api.multi
    def dashboard_late_employee_action_id(self):
        view = self.env.ref('gbs_hr_attendance_error_correction.hr_attendance_error_tree')
        res_emp_ids=[]
        if self.operating_unit_name:
            query = """select e.id from hr_employee e join operating_unit o on e.operating_unit_id=o.id where o.name=%s"""
            self._cr.execute(query, tuple([self.operating_unit_name]))
            res_emp_ids = self._cr.fetchall()
        attendance_pool = self.env['hr.attendance']
        att_ids = attendance_pool.search([('check_in', '>=', self.str_strt_dt),('check_in','<=',self.str_end_dt),('check_in','>',self.str_check_in),('employee_id','in',res_emp_ids)])

        return {
            'name': ('Late Employee'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'hr.attendance',
            'domain': [('id', '=', att_ids.ids)],
            'view_id': [view.id],
            'context': {'create': False,'edit': False},
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dashboard_absent_employee_action_id(self):
        view = self.env.ref('hr.view_employee_tree')
        res_emp_ids = []
        if self.operating_unit_name:
            query = """select e.id from hr_employee e join operating_unit o on e.operating_unit_id=o.id where o.name=%s"""
            self._cr.execute(query, tuple([self.operating_unit_name]))
            res_emp_ids = self._cr.fetchall()
        if res_emp_ids:
            query = """select e.id as id from hr_employee e
                        where e.id in %s
                        and e.id not in 
                        (select employee_id from hr_attendance
                        where employee_id in %s
                        and check_in between %s
                        and %s
                        group by employee_id)"""
            self._cr.execute(query, tuple([tuple(res_emp_ids),tuple(res_emp_ids),self.str_strt_dt,self.str_end_dt]))
            res_absent_emp_ids = self._cr.fetchall()

        return {
            'name': ('Absent Employee'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'hr.employee',
            'domain': [('id', 'in', res_absent_emp_ids)],
            'view_id': [view.id],
            'context': {'create': False},
            'type': 'ir.actions.act_window'
        }