from openerp import models, fields, api, exceptions


class ConfigureEmpChecklist(models.Model):
    _name = "hr.emp.master.checklists"

    employee_id = fields.Many2one('hr.employee', select=True, invisible=False,  default=lambda self: self._employee_gets())
    _rec_name = 'employee_id'
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done'), ('send', 'Send')], readonly=True, copy=False,
                             default='draft')
    checklist_status_ids = fields.One2many('hr.checklist.status', 'checklist_status_id')


    @api.multi
    def _employee_gets(self):

        ids = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        if ids:
            return ids[0]
        return False

    @api.multi
    def check_list_submit(self):
        # for record in self:
        #     if record.employee_id and record.employee_id.parent_id and record.employee_id.parent_id.user_id:
        #         self.message_subscribe_users([record.id], user_ids=[record.employee_id.parent_id.user_id.id])
        return self.write({'state': 'done'})

    @api.multi
    def check_list_reset(self):
        return self.write({'state': 'draft'})

    @api.multi
    def check_list_send(self):
        return self.write({'state': 'send'})

    @api.multi
    def _compute_check(self):
        return 1



