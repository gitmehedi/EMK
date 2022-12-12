from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError


class InheritedReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    return_date = fields.Date(string='Return Date', default=datetime.today())
    return_reason = fields.Char(string='Return Reason', limit=20)

    @api.multi
    def create_return_obj(self):
        for rec in self:
            # TODO: check if invoice created for this DC
            # TODO: _create_returns(self): this method functionality study

            picking = self.env['stock.picking'].browse(self.env.context['active_id'])
            return_moves = self.product_return_moves.mapped('move_id')
            print('picking', picking)
            print('return_moves', return_moves)
            print('return_date', rec.return_date)
            if not picking.partner_id.property_account_receivable_id:
                raise UserError(_("Receivable account not found for this customer!"))

            partner_acc_rec = picking.partner_id.property_account_receivable_id.id
            sale_journal_id = \
            self.env['account.journal'].search([('type', '=', 'sale'), ('company_id', '=', picking.company_id.id)])[0]
            if not picking.origin:
                raise UserError(
                    _("Source Document not found for this picking! \n Source Document contains the reference of sale order!"))
            sale_order_obj = self.env['sale.order'].search([('name', '=', picking.origin)])[0]
            refund_obj = {
                'number': self.env['ir.sequence'].sudo().next_by_code('account.invoice'),
                'name': rec.return_reason,
                'partner_id': picking.partner_id.id,
                'date_invoice': rec.return_date,
                'currency_id': sale_order_obj.currency_id.id,
                'sale_type_id': sale_order_obj.type_id.id,
                'type': 'out_refund',
                'user_id': self.env.user.id,
                'operating_unit_id': picking.operating_unit_id.id,
                'journal_id': sale_journal_id.id,
                'company_id': picking.company_id.id,
                'account_id': partner_acc_rec
            }
            invoice_obj = self.env['account.invoice'].create(refund_obj)

            # invoice_line = {
            #     'product_id':'',
            #     'name':'',
            #     'account_id':'',
            #     'quantity':'',
            #     'uom_id':'',
            #     'price_unit':'',
            #     'invoice_id':invoice_obj.id
            # }
            print('invoice_obj', invoice_obj)
