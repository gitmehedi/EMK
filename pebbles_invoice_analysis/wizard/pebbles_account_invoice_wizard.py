# -*- coding: utf-8 -*-
##############################################################################

from openerp import api, exceptions, fields, models

class PebblesAccountInvoiceWizard(models.TransientModel):

    """Refunds invoice"""
    _name = "pebbles.account.invoice.wizard"

    product_id = fields.Many2one('product.product', 'Product Name')
    partner_id = fields.Many2one('res.partner', 'Partner Name')
    category_id = fields.Many2one('product.category', 'Category of Product')



    @api.multi
    def invoice_create(self):
        context = {
            'product_id': self.product_id.id,
            'partner_id': self.partner_id.id,
            'category_id': self.category_id.id
        }

        # win_obj = self.env['ir.actions.act_window']
        # return win_obj.for_xml_id('pebbles_invoice_analysis', 'pebbles_view_account_invoice_report_graph', context)

        return {
            'view_type': 'pivot',
            'view_mode': 'graph',
            'res_model': 'pebbles.account.invoice.report',
            'view_id': 'pebbles_view_account_invoice_report_graph',
            'type': 'ir.actions.act_window',

            'context': context,
        }


