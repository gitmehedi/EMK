from odoo import api, fields, models,tools
from datetime import date


class HrAttendanceDashboard(models.Model):
    _name = "hr.attendance.dashboard"
    _auto = False

    operating_unit_name = fields.Char(string= 'Operating Unit')
    present_count = fields.Integer(string="Present")
    absent_count = fields.Integer(string="Absent")
    total_count = fields.Integer(string="Total")
    late_count = fields.Integer(string="Late")
    color = fields.Integer(string='Color Index', default=0)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'attendance_dashboard')
        current_date=date.today()
        str_current_date =current_date.strftime("%Y-%m-%d")
        str_end_dt = str_current_date + ' 23:59:59'
        str_strt_dt = str_current_date + ' 00:00:00'
        str_check_in =str_current_date + ' 03:15:00'

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
        self._cr.execute(query, tuple([str_strt_dt,str_end_dt,str_strt_dt,str_end_dt,str_check_in]))

