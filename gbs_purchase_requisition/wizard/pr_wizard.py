from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseRequisitionTypeWizard(models.TransientModel):
    _name = 'purchase.requisition.type.wizard'

    region_type = fields.Selection([('local', 'Local'), ('foreign', 'Foreign')],
                                   string="Region Type")

    purchase_by = fields.Selection([('cash', 'Cash'), ('credit', 'Credit'), ('lc', 'LC'), ('tt', 'TT')],
                                   string="Purchase By")

    @api.multi
    def save_type(self):
        if self.region_type == 'local' and self.purchase_by == 'tt':
            raise UserError(_(
                "Invalid Input" + "\nFor Foreign Purchase: Apply LC or TT. " + "\nLocal Purchase: Apply Cash, Credit or LC."))
        elif self.region_type == 'foreign' and (self.purchase_by == 'cash' or self.purchase_by == 'credit'):
            raise UserError(_(
                "Invalid Input" + "\nFor Foreign Purchase: Apply LC or TT. " + "\nLocal Purchase: Apply Cash, Credit or LC."))

        form_id = self.env.context.get('active_id')
        pr_form_pool = self.env['purchase.requisition'].search([('id', '=', form_id)])
        pr_form_pool.write(
            {'region_type': self.region_type,'purchase_by': self.purchase_by,'state': 'done'})
        po_pool_obj = self.env['purchase.order'].search([('requisition_id', '=', form_id)])
        if po_pool_obj:
            po_pool_obj.write({'check_po_action_button': True,
                               'region_type': self.region_type or False,
                               'purchase_by': self.purchase_by or False})
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










