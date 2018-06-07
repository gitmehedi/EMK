from odoo import models, fields, api


class HrLeaveCarryForwardWizard(models.TransientModel):
    _name = 'cheque.info.wizard'

    cheque_info_ids = fields.Many2many('cheque.info.entry', string='Cheque Info',
                                       domain="[('is_cheque_paid','=',False),('state','=','print')]")


    @api.multi
    def process_cheque_info_line(self, context):

        cheque_pay_obj = self.env['cheque.pay.confirmation'].search([('id', '=', context['active_id'])])

        for val in self.cheque_info_ids:
            vals = {}
            vals['partner_id'] = val.partner_id.id
            vals['amount'] = val.amount
            vals['cheque_number'] = val.cheque_number
            vals['cheque_date'] = val.cheque_date
            vals['parent_id'] = context['active_id']

            val.write({'is_cheque_paid': True})

            cheque_pay_obj.line_ids.create(vals)

