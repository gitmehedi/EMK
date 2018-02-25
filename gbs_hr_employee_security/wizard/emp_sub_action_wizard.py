from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class EmpSubActionWizard(models.TransientModel):
    _name = 'emp.sub.action.wizard'

    validation_level = fields.Integer(string='Validation Level')

    @api.multi
    def save_record(self):
        for lev in self:
            if lev.validation_level == 0:
                raise ValidationError(_('Chain level can not be zero !'))
        form_ids = self.env.context.get('active_ids')
        for form_id in form_ids:
            emp_form_pool = self.env['hr.employee'].search([('id', '=', form_id)])
            emp_form_pool.write({'validation_level': self.validation_level})

            for approver in emp_form_pool.holidays_approvers:
                approver.unlink()

            approver = emp_form_pool.parent_id
            sequence = 1
            pool_emp_approver_objs = self.env['hr.employee.holidays.approver']

            while sequence <= emp_form_pool.validation_level:
                if sequence == emp_form_pool.validation_level:
                    model_data_pool = self.env['ir.model.data'].search([('module','=','hr_holidays'),('name','=','group_hr_holidays_user')], limit=1)
                    record_id = model_data_pool.res_id
                    holiday_officer_group = self.env['res.groups'].search([('id','=',record_id)])
                    if holiday_officer_group and holiday_officer_group.users:
                        pool_emp_obj = self.env['hr.employee'].search([('user_id', 'in', holiday_officer_group.users.ids),('operating_unit_id','=',emp_form_pool.operating_unit_id.id)])
                        if pool_emp_obj:
                            emp_approver = (pool_emp_obj - emp_form_pool)
                            if emp_approver:
                                pool_emp_approver_objs.create(
                                    {'employee': emp_form_pool.id, 'approver': emp_approver[0].id, 'sequence': sequence})
                    sequence = sequence + 1
                elif approver:
                    pool_emp_approver_objs.create(
                        {'employee': emp_form_pool.id, 'approver': approver.id, 'sequence': sequence})
                    approver = approver.parent_id
                    sequence = sequence + 1
                else:
                    sequence = sequence + 1
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def set_default_validation_chain(self):
        form_ids = self.env.context.get('active_ids')
        for form_id in form_ids:
            emp_form_pool = self.env['hr.employee'].search([('id', '=', form_id)])
            for approver in emp_form_pool.holidays_approvers:
                approver.unlink()

            approver = emp_form_pool.parent_id
            sequence = 1
            while True:
                if approver:
                    self.env['hr.employee.holidays.approver'].create(
                        {'employee': emp_form_pool.id, 'approver': approver.id, 'sequence': sequence})
                    approver = approver.parent_id
                    sequence = sequence + 1
                else:
                    break
        return {'type': 'ir.actions.act_window_close'}