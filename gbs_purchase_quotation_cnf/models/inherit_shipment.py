from odoo import api, fields, models,_

class ShipmentProduct(models.Model):
    _inherit = 'purchase.shipment'

    @api.multi
    def action_quotation(self):
        res = self.env.ref('gbs_purchase_quotation_cnf.view_cnf_quotation_form')
        result = {
            'name': _('Please Enter The Information'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'context': {'shipment_id': self.id or False,
                        'cnf_quotation': True,
                        'partner_id': self.cnf_id.id or False},
        }
        # self.state = 'cnf_quotation'
        return result

    @api.multi
    def action_approve_quotation(self):
        self.write({'state': 'approve_cnf_quotation'})
        # cnf_pool_obj = self.env['purchase.order'].search([('shipment_id', '=', self.id)])
        # cnf_pool_obj.cnf_button_confirm()

    @api.multi
    def action_to_quotation(self):
        self.write({'state': 'cnf_quotation'})
