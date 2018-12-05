from odoo import api, fields, models, _

class PurchaseRequisitionTypeWizard(models.TransientModel):
    _inherit = 'purchase.order.type.wizard'

    @api.multi
    def save_type(self):
        res = super(PurchaseRequisitionTypeWizard, self).save_type()
        if res:
            po_pick_objs = self.env['purchase.order'].search([('id', '=', self.env.context.get('active_id'))]).picking_ids
            if po_pick_objs:
                if self.purchase_by == 'cash':
                    po_pick_objs[0].write({'receive_type': 'other'})
                else:
                    po_pick_objs[0].write({'receive_type': self.purchase_by})
        return res










