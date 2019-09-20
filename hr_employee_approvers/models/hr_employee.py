from odoo import models, fields, api,_

class Employee(models.Model):
    _inherit ='hr.employee'

    # # Create Method
    @api.model
    def create(self, vals):
        res = super(Employee, self).create(vals)
        if res.user_id:
            if 'holidays_approvers' in vals:
                for approver in vals['holidays_approvers']:
                    approver_id = approver[2]['approver']
                    self._cr.execute('INSERT INTO hr_employee_res_users_rel (hr_employee_id,res_users_id) VALUES (%s, %s)',
                                     tuple([approver_id,res.user_id.id]))
        return res

    # Write Method
    @api.multi
    def write(self, vals):
        res = super(Employee, self).write(vals)
        if self.user_id:
            if 'holidays_approvers' in vals or self.holidays_approvers:
                self._cr.execute('delete from hr_employee_res_users_rel where res_users_id=%s',tuple([self.user_id.id,]))
                for approver in self.holidays_approvers:
                    self._cr.execute('INSERT INTO hr_employee_res_users_rel (hr_employee_id,res_users_id) VALUES (%s, %s)',
                                     tuple([approver.approver.id,self.user_id.id]))
        return res

    # Delete Method
    @api.multi
    def unlink(self):
        for emp in self:
            if emp.user_id:
                self._cr.execute('delete from hr_employee_res_users_rel where res_users_id=%s', tuple([emp.user_id.id, ]))
        return super(Employee, self).unlink()