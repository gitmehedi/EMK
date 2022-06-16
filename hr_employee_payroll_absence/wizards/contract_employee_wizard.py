from openerp import models, fields, api


class ContractEmployeeWizard(models.TransientModel):
    _name = 'contract.employee.wizard'

    employee_ids = fields.Many2many('hr.employee', string='Employees')

    @api.multi
    def process_employee_line(self, context):
        id = context['active_id']

        lines = self.env['hr.employee.payroll.absence.line'].search([('line_id', '=', id)])
        contract_employee = list(set(self.employee_ids.ids) - set([val.employee_id.id for val in lines]))

        for contract in contract_employee:
            lines.create({
                'employee_id': contract,
                'days': 0,
                'line_id': id,
            })

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'src_model': 'hr.employee.payroll.absence',
            'res_model': 'hr.employee.payroll.absence',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': id
        }
