from odoo import fields, models, api


class TempDepartmentAccount(models.TransientModel):
    _name = 'temp.department.account.map'
    _description = 'Temp Department Account Map'

    department_id = fields.Many2one('hr.department', string='Department')

    account_id = fields.Many2one('account.account', string='Debit Account')
    provision_id = fields.Many2one(comodel_name='hr.payslip.run.create.provision', ondelete='cascade',
                                   string='Provision',
                                   store="True")
