from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def get_lc_reference(self):
        for rec in self:
            if rec.so_id.lc_id:
                rec.lc_id = rec.so_id.lc_id

    lc_id = fields.Many2one('letter.credit', compute='get_lc_reference', string='LC No', readonly=True, search='_search_lc_id')

    @api.model
    def _search_lc_id(self, operator, value):
        res = []
        lc_ids = self.env['letter.credit'].search(
            [('name', operator, value)])

        so_ids = self.env['sale.order'].search(
            [('lc_id', 'in', lc_ids.ids)])

        invoice_ids = self.env['account.invoice'].search(
                [('so_id', 'in', so_ids.ids)])

        res.append(('id', 'in', invoice_ids.ids))
        return res
