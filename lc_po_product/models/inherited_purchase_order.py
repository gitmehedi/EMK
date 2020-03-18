from odoo import models, fields, api, _


class InheritedPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    lc_ids = fields.Many2many('letter.credit', 'po_lc_rel', 'po_id', 'lc_id', string='Letter Of Credit', copy=False)
    po_lc_id = fields.Many2one('letter.credit', string='LC/TT Number', compute='_compute_po_lc_id', readonly=True, store=False, search='_search_po_lc_id')

    @api.depends('lc_ids')
    def _compute_po_lc_id(self):
        for rec in self:
            if rec.lc_ids.ids:
                rec.po_lc_id = rec.lc_ids[0]

    @api.model
    def _search_po_lc_id(self, operator, value):
        res = []
        letter_credit_ids = self.env['letter.credit'].search([('name', operator, value)])
        purchase_order_ids = self.env['purchase.order'].search([('lc_ids', 'in', letter_credit_ids.ids)])
        res.append(('id', 'in', purchase_order_ids.ids))

        return res
