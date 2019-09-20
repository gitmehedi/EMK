from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError
import numpy as np

class LetterOfCreditCommon(models.Model):
    _inherit = "letter.credit"

    lc_document_line = fields.One2many('lc.document.line', 'lc_id', string='LC Documents')
    bank_code = fields.Char(string='Bank')
    bank_branch = fields.Char(string='Bank Branch')


    @api.multi
    def action_revision_export(self,amendment_date=None):
        self.ensure_one()
        view_ref = self.env['ir.model.data'].get_object_reference('lc_sales_product_local', 'view_lc_export_form')
        view_id = view_ref and view_ref[1] or False,
        self.with_context(new_lc_revision=True,amendment_date=amendment_date).copy()

        number = len(self.old_revision_ids)

        comm_utility_pool = self.env['commercial.utility']
        note = comm_utility_pool.getStrNumber(number) + ' ' + 'Amendment'

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
        res = self.env.ref('lc_sales_product_local.view_shipment_export_form')
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


    @api.multi
    def action_amendment(self):
        res = self.env.ref('lc_sales_product_local.lc_amendment_wizard')
        result = {
            'name': _('Please Enter The Information'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'lc.amendment.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result




