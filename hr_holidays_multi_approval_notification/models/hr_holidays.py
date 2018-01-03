from odoo import api, fields,models, SUPERUSER_ID, _
from odoo.exceptions import ValidationError,UserError


class Holidays(models.Model):
    _inherit = 'hr.holidays'

    @api.one
    @api.constrains('number_of_days_temp')
    def _check_values(self):
        if self.number_of_days_temp == 0.0:
            raise ValidationError(_('Duration time should not be zero!!'))

    @api.model
    def create(self, vals):
        res = super(Holidays, self).create(vals)
        res._notify_approvers()
        return res

    @api.multi
    def write(self, values):
        employee_id = values.get('employee_id', False)
        if employee_id:
            self.pending_approver = self.env['hr.employee'].search([('id','=',employee_id)]).holidays_approvers[0].approver.id
        res = super(Holidays, self).write(values)
        return res


    @api.multi
    def _notify_approvers(self):
        """Input: res.user"""
        # self.ensure_one()
        for holiday in self:
            approvers = holiday.employee_id._get_employee_manager()
            if not approvers:
                return True
            for approver in approvers:
                holiday.sudo(SUPERUSER_ID).add_follower(approver.id)
                if approver.sudo(SUPERUSER_ID).user_id:
                    holiday.sudo(SUPERUSER_ID)._message_auto_subscribe_notify(
                        [approver.sudo(SUPERUSER_ID).user_id.partner_id.id])
        return True

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