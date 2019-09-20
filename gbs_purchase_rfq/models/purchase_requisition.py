from odoo import api, fields, models,_

class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    def action_send_rfq(self):
        res = self.env.ref('gbs_purchase_rfq.rfq_wizard_form')

        result = {
            'name': _('RFQ'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'rfq.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }

        return result

