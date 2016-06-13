from openerp import models, fields, api, exceptions
from openerp.osv import osv


class EmployeeExitReq(models.Model):
    _name = 'hr.emp.exit.req'

    _rec_name = 'employee_id'
    descriptions = fields.Text(string='Descriptions', required=True)
    emp_notes = fields.Char(size=300, string='Employee Notes', )
    department_notes = fields.Char(size=300, string='Department Manager Notes')
    hr_notes = fields.Char(size=300, string='HR Manager Notes')
    manager_notes = fields.Char(size=300, string='General Manager Notes')
    req_date = fields.Date(string='Request Date', required=True)
    last_date = fields.Date(string='Last Day of Work', required=True)
    state = fields.Selection(
        [('draft', 'To Submit'), ('cancel', 'Cancelled'), ('confirm', 'To Approve'), ('refuse', 'Refused'),
         ('validate1', 'Second Approval'), ('validate2', 'Third Approval'), ('validate', 'Approved')],
        'Status', readonly=True, copy=False, default='draft',
        help='The status is set to \'To Submit\', when a Exit request is created.\
            \nThe status is \'To Approve\', when exit request is confirmed by user.\
            \nThe status is \'Refused\', when exit request is refused by manager.\
            \nThe status is \'Approved\', when exit request is approved by manager.')

    employee_id = fields.Many2one('hr.employee', select=True, invisible=False)
    job_id = fields.Many2one('hr.job', string='Job Title')
    user_id = fields.Float(compute='_compute_user_id')
    manager_id = fields.Many2one('hr.employee', invisible=False, copy=False,
                                 help='This area is automatically filled by the user who validate the exit process')

    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id')

    category_id = fields.Many2one('hr.employee.category', string='Category', help='Category of Employee')
    manager_id2 = fields.Many2one('hr.employee', string='Second Approval', readonly=True, copy=False,
                                  help='This area is automaticly filled by the user who validate the exit with second level (If exit type need second validation)')
    manager_id3 = fields.Many2one('hr.employee', string='Third Approval', readonly=True, copy=False,
                                  help='This area is automaticly filled by the user who validate the exit with third level (If exit type need third validation)')
    parent_id = fields.Many2one('hr.emp.exit.req', string='Parent')
    linked_request_ids = fields.One2many('hr.emp.exit.req', 'parent_id', 'Linked Requests', ),

    # can_reset = fields.Boolean(compute='_get_can_reset')


    @api.multi
    def _get_can_reset(self):

        # user can edit the exit request if it is draft/to approve stage
        result = False

        return result

    @api.multi
    @api.depends('employee_id')
    def _compute_user_id(self):
        return 1

    @api.multi
    @api.depends('employee_id')
    def _compute_department_id(self):
        return 1

    # class Inherit_hr_employee(models.Model):
    #     _inherit = "hr.employee"




    @api.multi
    def exit_reset(self):
        self.write({'state': 'draft', 'manager_id': False, 'manager_id2': False})
        # to_unlink = []
        # for record in self.browse(self.ids):
        #     # for record2 in record.linked_request_ids:
        #     #     self.exit_reset()
        #     to_unlink.append(record.id)
        # if to_unlink:
        #     self.unlink(to_unlink)
        return True

    @api.multi
    def exit_confirm(self):
        for record in self:
            if record.employee_id and record.employee_id.parent_id and record.employee_id.parent_id.user_id:
                self.message_subscribe_users([record.id], user_ids=[record.employee_id.parent_id.user_id.id])
        return self.write({'state': 'confirm'})

    @api.multi
    def exit_validate(self):
        obj_emp = self.env['hr.employee']
        ids2 = obj_emp.search([('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        self.write({'state': 'validate'})

        return True

    @api.multi
    def exit_first_validate(self):
        obj_emp = self.env['hr.employee']
        ids2 = obj_emp.search([('user_id', '=', self.id)])
        manager = ids2 and ids2[0] or False
        self.exit_first_validate_notificate()
        return self.write({'state': 'validate1', 'manager_id': manager})

    @api.multi
    def exit_first_validate_notificate(self):
        for obj in self:
            self.message_post("Request approved, waiting second validation.")

    @api.multi
    def exit_refuse(self):
        obj_emp = self.env['hr.employee']
        ids2 = obj_emp.search([('user_id', '=', self.id)])
        manager = ids2 and ids2[0] or False
        for emp_exit in self:
            if emp_exit.state == 'validate1':
                self.write({'state': 'refuse', 'manager_id': manager, 'exit_id': emp_exit.id})
            else:
                self.write({'state': 'refuse', 'manager_id2': manager, 'exit_id': emp_exit.id})
        self.exit_cancel()
        return True

    @api.multi
    def exit_cancel(self):
        for record in self:
            # Delete the meeting
            if record.meeting_id:
                record.meeting_id.unlink()

            # If a category that created several exits, cancel all related
            self.signal_workflow(map(attrgetter('id'), record.linked_request_ids or []), 'refuse')

       # self._remove_resource_exit()
        return True

    @api.multi
    def _remove_resource_exit(self):
        '''This method will create entry in resource calendar leave object at the time of holidays cancel/removed'''
        obj_res_exit = self.env['resource.calendar.leaves']
        leave_ids = obj_res_exit.search([('holiday_id', 'in', ids)])
        return obj_res_exit.unlink(leave_ids)

    @api.multi
    def write(self, vals):
        employee_id = vals.get('employee_id', False)
        if vals.get('state') and vals['state'] not in ['draft', 'confirm', 'cancel']:
            raise osv.except_osv(_('Warning!'), _(
                'You cannot set a exit request as \'%s\'. Contact a human resource manager.') % vals.get('state'))
        hr_exit_id = super(EmployeeExitReq, self).write(vals)
        return hr_exit_id

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state not in ['draft', 'cancel', 'confirm']:
                raise osv.except_osv(_('Warning!'), _('You cannot delete! It is in %s state.') % (rec.state))
        return super(EmployeeExitReq, self).unlink()
