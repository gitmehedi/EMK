from odoo import fields, models, api


class InheritedAccountInvoice(models.Model):
    _inherit = "account.invoice"
    _description = 'Inherited Account Invoice'

    @api.model
    def create(self, vals):
        if 'so_id' in vals and 'journal_id' in vals:
            sale_order_obj = self.env['sale.order'].browse(vals['so_id'])
            journal_obj = self.env['account.journal'].browse(vals['journal_id'])

            if sale_order_obj and journal_obj:
                if sale_order_obj.company_id and journal_obj.company_id:
                    if sale_order_obj.company_id.id != journal_obj.company_id.id:
                        vals['company_id'] = sale_order_obj.company_id.id
                        journal_obj.sudo().write({'company_id': sale_order_obj.company_id.id})

        return super(InheritedAccountInvoice, self).create(vals)
