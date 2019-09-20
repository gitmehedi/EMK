from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ActHolidaysApprovedWizard(models.TransientModel):
    _name = 'act.holidays.approved.wizard'

    @api.multi
    def set_approver(self):
        form_ids = self.env.context.get('active_ids')
        for form_id in form_ids:
            hr_holiday_pool = self.env['hr.holidays'].search([('id', '=', form_id)])
            if hr_holiday_pool.employee_id.holidays_approvers:
                if hr_holiday_pool.state != 'confirm':
                    hr_holiday_pool.state = 'confirm'

                emp_approver = hr_holiday_pool.employee_id.holidays_approvers[0].approver.id
                hr_holiday_pool.pending_approver = emp_approver
            else:
                raise ValidationError(_('Please!! At First Set Approver Level For %s .')% (hr_holiday_pool.employee_id.name_related))

        return {'type': 'ir.actions.act_window_close'}

