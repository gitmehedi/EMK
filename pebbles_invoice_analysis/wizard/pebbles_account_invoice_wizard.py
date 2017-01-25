# -*- coding: utf-8 -*-
##############################################################################

from openerp import api, exceptions, fields, models

class PebblesAccountInvoiceWizard(models.TransientModel):

    """ Invoice Analysis Wizard"""
    _name = "pebbles.account.invoice.wizard"
    
    category_id = fields.Many2one('product.category', 'Product Category')
    product_id = fields.Many2one('product.product', 'Product', 
                                 domain="[('categ_id', '=', category_id)]")
    partner_id = fields.Many2one('res.partner', 'Partner', 
                                 domain="[('customer', '=', True)]")

    @api.multi
    def invoice_create(self):
        
        vals = {}
        
        if self.category_id:
            vals['category_id'] = str(self.category_id.id)
        else:
            vals['category_id'] = False
        if self.product_id:
            vals['product_id'] = str(self.product_id.id)
        else:
            vals['product_id'] = False
        if self.partner_id:
            vals['partner_id'] = str(self.partner_id.id)
        else:
            vals['partner_id'] = False
        
        invoice_pool = self.env['pebbles.account.invoice.report']
        invoice_pool.generate_invoice_analysis_data(vals)
        
        view_id = self.env.ref('pebbles_invoice_analysis.pebbles_view_account_invoice_report_graph').id

        # win_obj = self.env['ir.actions.act_window']
        # return win_obj.for_xml_id('pebbles_invoice_analysis', 'pebbles_view_account_invoice_report_graph', context)

        return {
            'name': 'Invoice Analysis',
            'view_type': 'pivot',
            'view_mode': 'graph',
            'res_model': 'pebbles.account.invoice.report',
            'view_id': view_id,
            'views': [(view_id, 'graph')],
            'type': 'ir.actions.act_window',
            'target': 'current',
            
        }


