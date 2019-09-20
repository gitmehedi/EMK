from odoo import models, fields, _


class OrientationChecklist(models.Model):
    _name = 'orientation.checklist'
    _description = "Checklist"
    _rec_name = 'checklist_name'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    checklist_name = fields.Char(string='Name', required=True)
    checklist_department = fields.Many2one('hr.department', string='Department', required=True)
    active = fields.Boolean(string='Active', default=True,
                            help="Set active to false to hide the Orientation Checklist without removing it.")
    checklist_line_id = fields.One2many('orientation.check', 'checklist', String="Checklist")


class OrientationChecklistNew(models.Model):
    _name = 'orientation.check'

    checklist_line_name = fields.Many2one('checklist.line', string='Name')
    checklist_line_user = fields.Many2one('res.users', string='Responsible User',
                                          related='checklist_line_name.responsible_user')
    expected_date = fields.Date(string="Expected Date", default=fields.Datetime.now)
    status = fields.Char(string='Status', readonly=True, default=lambda self: _('New'))
    checklist = fields.Many2one('orientation.checklist', string="Checklist", ondelete='cascade')
    relative_field = fields.Many2one('employee.orientation')




