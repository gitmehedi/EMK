from openerp import models, fields, api, _
from odoo.exceptions import ValidationError


class EmployeeCreditSaleWizard(models.TransientModel):
    _name = 'employee.credit.sale.wizard'

    def _get_amount(self):
        ctx = self.env.context
        order = self.env[ctx['active_model']].search([('id', '=', ctx['active_id'])])
        return order.amount_total

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    credit_amount = fields.Float(string='Credit Amount', required=True, default=_get_amount)

    @api.multi
    def process_credit_sale(self, ctx):
        order = self.env[ctx['active_model']].search([('id', '=', ctx['active_id'])])

        credit_sale = self.env['hr.ted.cafe.credit.sale'].search([('state', '=', 'approve')])
        if not credit_sale:
            raise ValidationError(_("Please create an active credit sale for this month"))

        credit = {
            'employee_id': self.employee_id.id,
            'date': order.date_order,
            'pos_id': order.id,
            'amount': self.credit_amount,
            'state': 'applied',
            'line_id': credit_sale.id,
        }
        line = credit_sale.line_ids.create(credit)
        order.write({'credit_sale_id': line.id})

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'src_model': 'pos.order',
            'res_model': 'pos.order',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': ctx['active_id']
        }
