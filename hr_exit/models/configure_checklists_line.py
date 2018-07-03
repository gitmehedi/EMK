from odoo import models, fields, api, exceptions

class ConfigureChecklistsLine(models.Model):
    _name = "hr.exit.configure.checklists.line"

    status_line_id = fields.Many2one('hr.checklist.status')
    checklist_item_id = fields.Many2one('hr.exit.checklist.item', domain=[('is_active','=',True)],
                                        string='Checklist Item', required=True)

    # Relational fields
    checklists_id = fields.Many2one('hr.exit.configure.checklists')
    responsible_department = fields.Many2one('hr.department', ondelete='set null', string='Responsible Department',compute='_checkApp')
    responsible_emp = fields.Many2one('hr.employee', string='Responsible User',compute='_checkApp')


    @api.one
    def _checkApp(self):
        if self.checklists_id.responsible_userdepartment_id:
            self.responsible_department = self.checklists_id.responsible_userdepartment_id
        elif self.checklists_id.responsible_username_id:
            self.responsible_emp = self.checklists_id.responsible_username_id
        else:
            pass

