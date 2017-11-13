from openerp.osv import osv
from openerp import models, fields, api
from openerp.tools.translate import _


class InheritedPuchaseOrder(models.Model):
    _inherit = 'purchase.order'

    invoice_status = fields.Boolean(string='Payment Complate', default=False, compute='compute_invoice_status')

    @api.multi
    def compute_invoice_status(self):
        for record in self:
            if not record.invoice_status:
                inv_sum = sum([invoice.amount_total for invoice in record.invoice_ids])
                if inv_sum == record.amount_total:
                    record.invoice_status = True
                    # record.write({'invoice_status': True})

    def manual_invoice(self, cr, uid, ids, context=None):
        """ create invoices for the given sales orders (ids), and open the form
            view of one of the newly created invoices
        """
        purchse_obj = self.pool.get('purchase.order')
        inv_line_obj = self.pool.get('account.invoice.line')
        ir_property_obj = self.pool.get('ir.property')
        fiscal_obj = self.pool.get('account.fiscal.position')
        mod_obj = self.pool.get('ir.model.data')

        # create invoices through the sales orders' workflow
        inv_ids0 = set(inv.id for purchase in self.browse(cr, uid, ids, context) for inv in purchase.invoice_ids)
        # self.signal_workflow(cr, uid, ids, 'manual_invoice')
        for purchase in purchse_obj.browse(cr, uid, ids, context=context):
            val = inv_line_obj.product_id_change(cr, uid, [], False,
                                                 False, partner_id=purchase.partner_id.id,
                                                 fposition_id=purchase.fiscal_position.id,
                                                 company_id=purchase.company_id.id)
            res = val['value']

            # determine and check income account

            prop = ir_property_obj.get(cr, uid,
                                       'property_account_expense_categ', 'product.category', context=context)
            prop_id = prop and prop.id or False
            account_id = fiscal_obj.map_account(cr, uid, purchase.fiscal_position or False, prop_id)
            if not account_id:
                raise osv.except_osv(_('Configuration Error!'),
                                     _('There is no expense account defined as global property.'))
            res['account_id'] = account_id
            if not res.get('account_id'):
                raise osv.except_osv(_('Configuration Error!'),
                                     _('There is no expense account defined for this product: "%s" (id:%d).'))

            inv_values = {
                'name': purchase.name,
                'origin': purchase.name,
                'type': 'in_invoice',
                'reference': False,
                'account_id': purchase.partner_id.property_account_payable.id,
                'partner_id': purchase.partner_id.id,
                'currency_id': purchase.pricelist_id.currency_id.id,
                'comment': purchase.notes,
                'payment_term': purchase.payment_term_id.id,
                'fiscal_position': purchase.fiscal_position.id or purchase.partner_id.property_account_position.id,
            }
            inv_obj = self.pool.get('account.invoice')
            inv_line_obj = self.pool.get('account.invoice.line')
            context['type'] = 'in_invoice'
            inv_id = inv_obj.create(cr, uid, inv_values, context=context)
            inv_line_values = []

            for line in purchase.order_line:
                values = {
                    'name': line.product_id.name,
                    'origin': purchase.name,
                    'account_id': res['account_id'],
                    'price_unit': line.price_unit,
                    'quantity': line.product_qty or 1.0,
                    'discount': False,
                    'uos_id': res.get('uos_id', False),
                    # 'product_id': line.product_id.id,
                    'invoice_line_tax_id': res.get('invoice_line_tax_id'),
                    'invoice_id': inv_id,
                }
                inv_line_obj.create(cr, uid, values, context=context)

            for invoice in purchase.invoice_ids:
                invoice_values = {
                    'name': invoice.invoice_line.name,
                    'origin': invoice.invoice_line.name,
                    'account_id': res['account_id'],
                    'price_unit': -invoice.invoice_line.price_unit,
                    'quantity': invoice.invoice_line.quantity or 1.0,
                    'discount': False,
                    'uos_id': res.get('uos_id', False),
                    # 'product_id': invoice.invoice_line.product_id.id,
                    'invoice_line_tax_id': res.get('invoice_line_tax_id'),
                    'invoice_id': inv_id
                }
                inv_line_obj.create(cr, uid, invoice_values, context=context)

                # purchase_obj = self.pool.get('purchase.order')
                # context['type'] = 'in_invoice'

                # inv_obj.button_reset_taxes(cr, uid, [inv_id], context=context)
                # add the invoice to the sales order's invoices
                purchse_obj.write(cr, uid, purchase.id, {'invoice_ids': [(4, inv_id)]}, context=context)

        # inv_ids1 = set(inv.id for purchase in self.browse(cr, uid, ids, context) for inv in purchase.invoice_ids)
        # determine newly created invoices
        # new_inv_ids = list(inv_ids1 - inv_ids0)

        res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
        res_id = res and res[1] or False,

        return {
            'name': _('Supplier Invoices'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': 'account.invoice',
            'context': "{'type':'in_invoice'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': inv_id or False,
        }
