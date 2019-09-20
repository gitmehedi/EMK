import datetime
from odoo import api, fields, models, _

class Employee(models.Model):
    _inherit = "hr.employee"

    remaining_leaves = fields.Float(compute='_compute_remaining_leaves', string='Remaining Legal Leaves',
                                    inverse='_inverse_remaining_leaves',
                                    help='Total number of legal leaves allocated to this employee, change this value to create allocation/leave request. '
                                         'Total based on all the leave types without overriding limit.')
    leaves_count = fields.Integer('Number of Leaves', compute='_compute_leaves_count')

    def _get_remaining_leaves(self):
        """ Helper to compute the remaining leaves for the current employees
            :returns dict where the key is the employee id, and the value is the remain leaves
        """
        year_id = self.get_year()
        self._cr.execute("""
            SELECT
                sum(h.number_of_days) AS days,
                h.employee_id
            FROM
                hr_holidays h
                join hr_holidays_status s ON (s.id=h.holiday_status_id)
            WHERE
                h.state='validate' AND
                s.limit=False AND
                h.employee_id in %s AND
                h.leave_year_id = %s
            GROUP BY h.employee_id,h.leave_year_id""", (tuple(self.ids),year_id,))
        return dict((row['employee_id'], row['days']) for row in self._cr.dictfetchall())

    @api.multi
    def _compute_remaining_leaves(self):
        remaining = self._get_remaining_leaves()
        for employee in self:
            employee.remaining_leaves = remaining.get(employee.id, 0.0)

    @api.multi
    def _compute_leaves_count(self):
        remaining = self._get_remaining_leaves()
        for employee in self:
            employee.leaves_count = remaining.get(employee.id)


    def get_year(self):
        year_id = 0
        curr_date = datetime.date.today().strftime('%Y-%m-%d')
        self.env.cr.execute(
            "SELECT * FROM hr_leave_fiscal_year  WHERE '{}' between date_start and date_stop".format(curr_date))
        years = self.env.cr.dictfetchone()
        if years:
            year_id = years['id']
        return year_id