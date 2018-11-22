# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_add_pq(self):
        res = self.env.ref('gbs_po_merge.po_merge_wizard_form')

        result = {
            'name': _('Add'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'po.merge.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {'default_is_new_add': True,
                        'operating_unit_id': self.operating_unit_id.id,
                        'partner_id': self.partner_id.id,
                        }
        }

        return result