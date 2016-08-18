from openerp import models, fields, api, exceptions
from openerp.osv import osv


class ConfigureEmpChecklist(models.Model):
    _name = "hr.emp.master.checklists"

    employee_id = fields.Many2one('hr.employee',string='Employee', select=True, invisible=False,  default=lambda self: self._employee_gets())
    _rec_name = 'employee_id'
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done'), ('send', 'Send'), ('verify', 'Verified')], readonly=True, copy=False,
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
    def check_list_verify(self):
        return self.write({'state': 'verify'})


    @api.multi
    def _compute_check(self):
        return 1

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state not in ['draft', 'done', 'send']:
                #raise UserError(_('You cannot delete a request which is in %s state.') % (rec.state,))
                raise osv.except_osv(('Error'), ('You cannot delete a request which is in %s state') % (rec.state))
        return super(ConfigureEmpChecklist, self).unlink()



