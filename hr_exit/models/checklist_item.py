from openerp import models, fields, api, exceptions


class ChecklistItem(models.Model):
    _name = 'hr.exit.checklist.item'

    # Model Fields
    # _rec_name = 'employee_id'
    # employee_id = fields.Many2one('hr.employee', select=True, invisible=False,
    #                               default=lambda self: self._employee_gets())
    name = fields.Char(string='Item Name', size=100, required=True, help='Please enter name.')
    description = fields.Text(string='Description', size=500, help='Please enter description.')
    is_active = fields.Boolean(string='Active', default=True)

    # Relational Fields
    checklist_type = fields.Many2one('hr.exit.checklist.type', ondelete='set null',
                                     string='Checklist Type', required=True, help='Please select checklist type.')
    #
    # keeper = fields.Many2one('hr.employee', ondelete='set null', string='Item Keeper', required=True,
    #                          help='Please enter item keeper name.')

    @api.multi
    def _employee_gets(self):
        # emp_id = context.get('default_employee_id', False)
        # if emp_id:
        #     return emp_id
        ids = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        if ids:
            return ids[0]
        return False
