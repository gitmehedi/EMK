from odoo import api, fields, models, SUPERUSER_ID
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def _get_employee_manager(self):
        manager = []
        for emp in self:
            if emp.holidays_approvers:
                for holidays_approver in emp.holidays_approvers:
                    manager.append(holidays_approver.approver)
            return manager