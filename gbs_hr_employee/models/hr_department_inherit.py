from odoo import fields, models, api, _
from odoo.exceptions import UserError

class HrDepartment(models.Model):
    _inherit = 'hr.department'

    @api.multi
    def unlink(self):
        for rec in self:
            department_obj = self.env['hr.employee'].search([('department_id', '=', self.id)])
            if department_obj:
                raise UserError(_('You cannot delete a record which has reference!'))
        return super(HrDepartment, self).unlink()