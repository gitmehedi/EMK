from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError
from openerp.addons.commercial.models.utility import Status, UtilityNumber

class LetterOfCredit(models.Model):
    _inherit = "letter.credit"


    @api.multi
    def action_confirm_export(self):
        self.write({'state': 'confirmed', 'last_note': Status.CONFIRM.value})

    @api.multi
    def action_revision_export(self):
        self.ensure_one()
        view_ref = self.env['ir.model.data'].get_object_reference('lc_sales_product', 'view_lc_export_form')
        view_id = view_ref and view_ref[1] or False,
        self.with_context(new_lc_revision=True).copy()

        number = len(self.old_revision_ids)

        comm_utility_pool = self.env['commercial.utility']
        note = comm_utility_pool.getStrNumber(number) + ' ' + Status.AMENDMENT.value

        self.write({'state': self.state, 'last_note': note})
        return {
            'type': 'ir.actions.act_window',
            'name': _('LC'),
            'res_model': 'letter.credit',
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
            'flags': {'initial_mode': 'edit'},
        }


    @api.multi
    def action_shipment_export(self):
        self.write({'state': 'progress'})
        res = self.env.ref('lc_sales_product.view_shipment_export_form')
        if not self.shipment_ids:
            shipmentNo = 1
        else:
            shipmentNo = len(self.shipment_ids) + 1

        comm_utility_pool = self.env['commercial.utility']

        result = {'name': _('Shipment'),
                  'view_type': 'form',
                  'view_mode': 'form',
                  'view_id': res and res.id or False,
                  'res_model': 'purchase.shipment',
                  'context': {'shipment_number': comm_utility_pool.getStrNumber(shipmentNo) + ' Shipment',
                              'lc_id': self.id,
                              'operating_unit_id': self.operating_unit_id.id,
                              'company_id': self.first_party.id},
                  'type': 'ir.actions.act_window',
                  'target': 'current'}
        self.env['letter.credit'].search([('id', '=', self.id)])
        return result

