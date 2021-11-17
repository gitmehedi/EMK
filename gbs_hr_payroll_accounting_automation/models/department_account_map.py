from odoo import fields, models, api


class DepartmentAccount(models.Model):
    _name = 'department.account.map'
    _description = 'Department Account Map'

    company_id = fields.Many2one('res.company', string='Company', store=True)

    # @api.model
    # def _default_departments(self):
    #     if self.operating_unit_id:
    #         print('operation obj', self.operating_unit_id)
    #     operation_obj = self._context.get('active_id')
    #     return self.env['hr.department'].search([('company_id', '=', operation_obj.company_id.id)])

    department_id = fields.Many2one('hr.department', string='Department')

    account_id = fields.Many2one('account.account', string='Debit Account')

    operating_unit_id = fields.Many2one(comodel_name='operating.unit', ondelete='cascade', string='Operating Unit',
                                        store="True")
