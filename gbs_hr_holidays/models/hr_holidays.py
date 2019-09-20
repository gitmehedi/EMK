from odoo import api, fields, models,_
from odoo.exceptions import UserError, AccessError, ValidationError

class HRHolidays(models.Model):
    _inherit = 'hr.holidays'

    first_approval = fields.Boolean('First Approval', compute='compute_check_first_approval')

    @api.one
    @api.constrains('number_of_days_temp')
    def _check_values(self):
        if self.number_of_days_temp == 0.0:
            raise ValidationError(_('Duration time should not be zero!!'))

    @api.multi
    def compute_check_first_approval(self):
        user = self.env.user.browse(self.env.uid)
        for h in self:
            if h.state != 'confirm':
                h.first_approval = False
            ### no one can approve own request
            elif h.employee_id.user_id.id == self.env.user.id:
                h.first_approval = False
            elif user.has_group('hr_holidays.group_hr_holidays_user'):
                h.first_approval = True
            else:
                res = h.employee_id.check_1st_level_approval()
                h.first_approval = res
                # h.first_approval = False

    @api.multi
    def action_refuse(self):
        if not (self.env.user.has_group('hr_holidays.group_hr_holidays_user')
                or self.env.user.has_group('gbs_application_group.group_dept_manager')):
            raise UserError(_('Only an HR Officer or Manager or Department Head can refuse leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate', 'validate1']:
                raise UserError(_('Leave request must be confirmed or validated in order to refuse it.'))

            if holiday.state == 'validate1':
                holiday.write({'state': 'refuse', 'manager_id': manager.id})
            else:
                holiday.write({'state': 'refuse', 'manager_id2': manager.id})
            # Delete the meeting
            if holiday.meeting_id:
                holiday.meeting_id.unlink()
            # If a category that created several holidays, cancel all related
            holiday.linked_request_ids.action_refuse()
        self._remove_resource_leave()
        return True