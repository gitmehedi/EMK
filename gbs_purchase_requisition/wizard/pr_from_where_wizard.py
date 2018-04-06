from odoo import api, fields, models, _


class PRFromWhereWizard(models.TransientModel):
    _name = 'pr.from.where.wizard'

    purchase_from = fields.Selection([('own', 'Own'), ('ho', 'HO')],
                                   string="Purchase From")
    @api.multi
    def save_type(self):
        form_id = self.env.context.get('active_id')
        pr_form_pool = self.env['purchase.requisition'].search([('id', '=', form_id)])
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










