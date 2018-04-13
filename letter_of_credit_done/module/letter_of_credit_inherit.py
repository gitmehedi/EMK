from odoo import api, fields, models,_
from odoo.exceptions import UserError,ValidationError



class LetterOfCreditInherit(models.Model):
    _inherit = 'letter.credit'

    lc_evaluation_lines = fields.One2many('lc.evaluation.line', 'rel_job_id', string='')
    comment = fields.Text(string='Comments')

    @api.multi
    def action_lc_eva_in_button(self):

        # Check Shipment Done or Not
        for shipment in self.shipment_ids:
            if shipment.state != 'done' and shipment.state != 'cancel':
                raise ValidationError(_("This LC has "+ str(len(self.shipment_ids)) +
                                        " shipment(s). Before Done this LC need to Done or Cancle all shipment(s)."))


        # Check Shipment Receive Product Quantiy
        product_line = []
        lc_pro_line = self.env['lc.product.line'].search([('lc_id', '=', self.id)])

        for obj in lc_pro_line:
            product_qty = obj.product_qty - obj.product_received_qty
            if product_qty > 0:
                product_line.append((0, 0, {'product_id': obj.product_id,
                                    'lc_pro_line_id': obj.id,
                                    'name': obj.name,
                                    'product_qty': product_qty,
                                    'currency_id': obj.currency_id,
                                    'date_planned': obj.date_planned,
                                    'product_uom': obj.product_uom,
                                    'price_unit': obj.price_unit,
                                    }))
        if len(product_line) > 0:
            res = self.env.ref('letter_of_credit_done.lc_done_confirmation_wizard')
            result = {
                'name': _('LC Done Confirmation'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': res and res.id or False,
                'res_model': 'lc.done.confirmation.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {'message': "LC Product Quantiy & Shipment Receive Quantiy are not same. Are you want to done the LC?", "lc_id": self.id},

            }
            return result

        # All Condition are done. Just evaluate the LC
        res = self.env.ref('letter_of_credit_done.lc_evaluation_wizard')
        result = {
            'name': _('LC Done'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'lc.evaluation.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {"lc_id": self.id},

        }
        return result

        ####################################################################################


    @api.multi
    def lc_done_action_window1(self):
        domain = [('rel_job_id', '=', self.id)]
        res = self.env.ref('letter_of_credit_done.lc_evaluation_wizard_button_box')
        result = {
            'name': _('LC Done'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'lc.evaluation.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': domain,
            'context': {'comment': self.comment or False, 'lc_id': self.id},
            'flags': {'form': {'action_buttons': False},},
        }
        return result

    @api.multi
    def action_confirm(self):
        res = super(LetterOfCreditInherit, self).action_confirm()
        pool_criteria_emp = self.env['lc.evaluation.line']
        for criteria in self.env['hr.employee.criteria'].search(
                [('is_active', '=', True), ('type', '=', 'lc_evaluation')]):
            criteria_res = {
                'name': criteria.name,
                'marks': criteria.marks,
                'rel_job_id': self.id,
            }
            pool_criteria_emp += self.env['lc.evaluation.line'].create(criteria_res)
        return res

    @api.multi
    def btn_approve(self):
        text = """The case """ + str(self.case_no) + """ will be forward to VC for further Approval. Are you want to proceed."""
        query = 'delete from thesis_approval_message_oric'
        self.env.cr.execute(query)
        value = self.env['thesis.approval.message.oric'].sudo().create({'text': text})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Message',
            'res_model': 'thesis.approval.message.oric',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            # 'context':{'thesis_obj':self.id,'flag':'course Work completed'},
            'res_id': value.id
        }