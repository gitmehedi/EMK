from odoo import fields, models, api


class DepartmentAccount(models.Model):
    _name = 'department.account.map'
    _description = 'Department Account Map'

    type = fields.Selection(
        [('regular', "Regular Salary"),
         ('festival_bonus', "Festival Bonus")], readonly=True)

    company_id = fields.Many2one('res.company', string='Company')

    department_id = fields.Many2one('hr.department', string='Department')

    account_id = fields.Many2one('account.account', string='Debit Account')

    operating_unit_id = fields.Many2one(comodel_name='operating.unit', ondelete='cascade', string='Operating Unit',
                                        store="True")

    festival_operating_unit_id = fields.Many2one(comodel_name='operating.unit', ondelete='cascade', string='Operating Unit',
                                        store="True")
