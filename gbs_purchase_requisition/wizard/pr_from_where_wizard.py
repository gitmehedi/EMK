from odoo import api, fields, models, _


class PRFromWhereWizard(models.TransientModel):
    _name = 'pr.from.where.wizard'

    purchase_from = fields.Selection([('own', 'Own'), ('ho', 'HO')],
                                   string="Purchase From")
    @api.multi
    def save_type(self):
        form_id = self.env.context.get('active_id')
        pr_form_pool = self.env['purchase.requisition'].search([('id', '=', form_id)])
        if self.purchase_from == 'own':
            pr_form_pool.write(
                {'purchase_from': self.purchase_from})
            # pr_form_pool.action_approve()
            res = self.env.ref('gbs_purchase_requisition.purchase_requisition_type_wizard')
            result = {
                'name': _('Please Select Region Type and Purchase By before approve'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': res and res.id or False,
                'res_model': 'purchase.requisition.type.wizard',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'context': {'active_id': pr_form_pool.id},
            }
            return result
        else:
            pr_form_pool.write(
                {'purchase_from': self.purchase_from, 'state': 'approve_head_procurement'})

            return {'type': 'ir.actions.act_window_close'}


    #
    # @api.multi
    # def cancel_window(self):
    #     form_id = self.env.context.get('active_id')
    #     pr_form_pool = self.env['purchase.requisition'].search([('id', '=', form_id)])
    #     pr_form_pool.write({'state': 'done'})
    #     po_pool_obj = self.env['purchase.order'].search([('requisition_id', '=', form_id)])
    #     if po_pool_obj:
    #         po_pool_obj.write({'check_po_action_button': True})
    #     return {'type': 'ir.actions.act_window_close'}










