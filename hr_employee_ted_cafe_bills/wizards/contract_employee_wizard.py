from openerp import models, fields, api


class ContractEmployeeTedWizard(models.TransientModel):
    _name = 'contract.employee.ted.wizard'

    employee_ids = fields.Many2many('hr.employee', string='Employees')

    @api.multi
    def process_employee_line(self, context):
        id = context['active_id']

        lines = self.env['hr.ted.cafe.bill'].search([('line_id', '=', id)])
        contract_employee = list(set(self.employee_ids.ids) - set([val.employee_id.id for val in lines]))

        for contract in contract_employee:
            lines.create({
                'employee_id': contract,
                'date': fields.Datetime.today(),
                'line_id': id,
            })

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'src_model': 'hr.ted.cafe.bill',
            'res_model': 'hr.ted.cafe.bill',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': id
        }
