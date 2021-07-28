#-*- coding:utf-8 -*-
from odoo import models, fields, api

class Holidays(models.Model):
    _name = "hr.holidays"
    _inherit = "hr.holidays"

    @api.multi
    def _default_approver(self):
        default_approver= 0
        employee = self._default_employee()
        if isinstance(employee,int):
            emp_obj = self.env['hr.employee'].search([('id', '=', employee)], limit=1)
            if emp_obj.sudo().holidays_approvers:
                default_approver = emp_obj.sudo().holidays_approvers[0].approver.id
        else:
            if employee.sudo().holidays_approvers:
                default_approver = employee.sudo().holidays_approvers[0].approver.id
        return default_approver

    pending_approver = fields.Many2one('hr.employee', string="Pending Approver", readonly=True, default=_default_approver)
    pending_approver_user = fields.Many2one('res.users', string='Pending approver user', related='pending_approver.user_id', related_sudo=True, store=True, readonly=True)
    current_user_is_approver = fields.Boolean(string= 'Current user is approver', compute='_compute_current_user_is_approver')
    approbations = fields.One2many('hr.employee.holidays.approbation', 'holidays', string='Approvals', readonly=True)
    pending_transfered_approver_user = fields.Many2one('res.users', string='Pending transfered approver user', compute="_compute_pending_transfered_approver_user", search='_search_pending_transfered_approver_user')

    @api.model
    def create(self, values):
        if values.get('employee_id', False):
            employee = self.env['hr.employee'].browse(values['employee_id'])
            if employee and employee.holidays_approvers and employee.holidays_approvers[0]:
                values['pending_approver'] = employee.holidays_approvers[0].approver.id
        res = super(Holidays, self).create(values)
        return res

    @api.onchange('employee_id')
    def _onchange_employee(self):
        if self.employee_id and self.employee_id.holidays_approvers:
            self.pending_approver = self.employee_id.holidays_approvers[0].approver.id
        else:
            self.pending_approver = False

    @api.multi
    def action_confirm(self):
        super(Holidays, self).action_confirm()
        for holiday in self:
            if holiday.employee_id.holidays_approvers:
                holiday.pending_approver = holiday.employee_id.holidays_approvers[0].approver.id
    
    @api.multi
    def btn_action_approve(self):
        for holiday in self:
            is_last_approbation = False
            sequence = 0
            next_approver = None
            for approver in holiday.employee_id.holidays_approvers:
                sequence = sequence + 1
                if holiday.pending_approver.id == approver.approver.id:
                    if sequence == len(holiday.employee_id.holidays_approvers):
                        is_last_approbation = True
                    else:
                        next_approver = holiday.employee_id.holidays_approvers[sequence].approver
            if holiday.type == 'add' and holiday.parent_id:
                is_last_approbation = True
            if is_last_approbation:
                holiday.action_validate()
            else:
                vals = {'state': 'confirm'}
                if next_approver and next_approver.id:
                    vals['pending_approver'] = next_approver.id
                holiday.write(vals)
                self.env['hr.employee.holidays.approbation'].create({'holidays': holiday.id, 'approver': self.env.uid, 'sequence': sequence, 'date': fields.Datetime.now()})
            
    @api.multi
    def action_validate(self):
        self.write({'pending_approver': None})
        for holiday in self:
            self.env['hr.employee.holidays.approbation'].create({'holidays': holiday.id, 'approver': self.env.uid, 'date': fields.Datetime.now()})
            if holiday.holiday_type == 'category':
                if holiday.double_validation:
                    if holiday.state == 'confirm':
                        super(Holidays, self).action_approve()
                    elif holiday.state == 'validate1':
                        super(Holidays, self).action_validate()
                else:
                    super(Holidays, self).action_validate()
            else:
                super(Holidays, self).action_validate()
    
    @api.one
    def _compute_current_user_is_approver(self):
        if self.pending_approver.user_id.id == self.env.user.id or self.pending_approver.transfer_holidays_approvals_to_user.id == self.env.user.id :
            self.current_user_is_approver = True
        else:
            self.current_user_is_approver = False
            
    @api.one
    def _compute_pending_transfered_approver_user(self):
        self.pending_transfered_approver_user = self.pending_approver.transfer_holidays_approvals_to_user
    
    def _search_pending_transfered_approver_user(self, operator, value):
        replaced_employees = self.env['hr.employee'].search([('transfer_holidays_approvals_to_user', operator, value)])
        employees_ids = []
        for employee in replaced_employees:
            employees_ids.append(employee.id)
        return [('pending_approver', 'in', employees_ids)]
