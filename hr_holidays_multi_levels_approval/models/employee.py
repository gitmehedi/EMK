#-*- coding:utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class Employee(models.Model):
    _inherit ='hr.employee'

    holidays_approvers = fields.One2many('hr.employee.holidays.approver', 'employee', string='Approvers chain')
    transfer_holidays_approvals_to = fields.Many2one('hr.employee', string='Transfer approval rights to')
    transfer_holidays_approvals_to_user = fields.Many2one('res.users', string='Transfer approval rights to user', related='transfer_holidays_approvals_to.user_id', related_sudo=True, store=True, readonly=True)

    validation_level = fields.Integer(string='Validation Level')

    @api.constrains('validation_level')
    def check_effective_date(self):
        if self.validation_level<0:
            raise ValidationError('Level Number can not negative!!!')

    @api.multi
    @api.one
    def set_default_validation_chain(self):
        for approver in self.holidays_approvers:
            approver.unlink()
        
        approver = self.parent_id
        sequence = 1
        while True:
            if approver:
                self.env['hr.employee.holidays.approver'].create({'employee': self.id, 'approver': approver.id, 'sequence': sequence})
                approver = approver.parent_id
                sequence = sequence + 1
            else:
                break

    @api.multi
    def set_custom_validation_chain(self):
        res = self.env.ref('hr_holidays_multi_levels_approval.custom_validation_level_wizard_view')
        result = {
            'name': _('Validation Level'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'custom.validation.level.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {'level': self.validation_level or False},
        }
        return result
    