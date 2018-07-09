from odoo import models, fields, api, exceptions,_
from odoo.exceptions import UserError, ValidationError



class ConfigureEmpChecklist(models.Model):
    _name = "hr.emp.master.checklists"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _rec_name = 'employee_id'
    responsible_type=fields.Selection(selection=[('department', 'Department'),('individual','Individual')],related='config_checklist_id.responsible_type',track_visibility='onchange')
    remarks= fields.Text('Remarks',required=True,track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done'), ('send', 'Send'), ('verify', 'Verified')],
                             readonly=True, copy=False,
                             default='draft', track_visibility='onchange')

    # Relational Fields
    config_checklist_id = fields.Many2one('hr.exit.configure.checklists', 'Checklist', required=True,track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee', string='Employee', select=True, required=True, invisible=False,track_visibility='onchange')
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id', track_visibility='onchange')
    responsible_userdepartment_id = fields.Many2one('hr.department', string='Responsible Department', track_visibility='onchange',
                                                    related='config_checklist_id.responsible_userdepartment_id')
    responsible_username_id = fields.Many2one('hr.employee', string='Responsible User',track_visibility='onchange',
                                              related='config_checklist_id.responsible_username_id')
    checklist_status_ids = fields.One2many('hr.checklist.status', 'checklist_status_id',track_visibility='onchange')

    # Onchange Function
    @api.onchange('config_checklist_id')
    def on_change_config_checklist_id(self):
        vals = []
        if self.config_checklist_id:
            confg_checklist_obj = self.env['hr.exit.configure.checklists'].search(
                [('id', '=', self.config_checklist_id.id)])
            for record in confg_checklist_obj:
                for config in record.checklists_ids:
                    vals.append((0, 0, {
                                        'checklist_status_item_id': config.checklist_item_id,
                                        'checklist_type_id': config.checklist_type,


                                        }))
                    self.checklist_status_ids = vals

    # Button Actions
    @api.multi
    def check_list_verify(self):
        exit_req_obj = self.env['hr.emp.exit.req'].search(
            [('employee_id', '=', self.employee_id.id),
             ('department_id', '=', self.department_id.id),('state','=','validate')])
        for exit_line in exit_req_obj.checklists_ids:
            if exit_line.responsible_department:
                if exit_line.responsible_department == self.responsible_userdepartment_id:
                    exit_line.remarks = self.remarks
                    exit_line.write({'state': 'received'})
            elif exit_line.responsible_emp:
                if exit_line.responsible_emp == self.responsible_username_id:
                    exit_line.remarks = self.remarks
                    exit_line.write({'state': 'received'})
            else:
                pass
        return self.write({'state': 'verify'})

    @api.multi
    def check_list_submit(self):
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

    @api.multi
    def unlink(self):
        for exitreq in self:
            if exitreq.state != 'draft':
                raise UserError(_('After done you can not delete this configuration checklist.'))
            exitreq.line_ids.unlink()
        return super(ConfigureEmpChecklist, self).unlink()