# imports of odoo
import json
from lxml import etree
from dateutil.relativedelta import relativedelta
import pytz
from datetime import datetime
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class ReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    available_qty = fields.Float("Available Quantity", digits=dp.get_precision('Product Unit of Measure'))


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _get_default_price_unit(self):
        price_unit = 0
        if 'active_id' in self.env.context:
            picking = self.env['stock.picking'].browse(self.env.context['active_id'])
            amount = sum(line.credit for line in picking.cogs_move_id.line_ids)
            price_unit = amount / picking.pack_operation_product_ids[0].qty_done

        return price_unit

    price_unit = fields.Float(string='COGS Unit Price', digits=dp.get_precision('Product Price'),
                              default=_get_default_price_unit)

    def _get_default_cogs_move(self):
        if 'active_id' in self.env.context:
            picking = self.env['stock.picking'].browse(self.env.context['active_id'])
            return picking.cogs_move_id.id
        else:
            return False

    cogs_move = fields.Many2one('account.move', default=_get_default_cogs_move)

    price_unit_text = fields.Float(string='COGS Unit Price', digits=dp.get_precision('Product Price'))

    @api.constrains('return_date')
    def _check_return_date(self):
        date = fields.Date.today()
        if self.return_date:
            if self.return_date > date:
                raise ValidationError(
                    "Return Date must be lesser than current date")

    return_date = fields.Date(string='Return Date', default=datetime.today())
    return_reason = fields.Char(string='Return Reason', size=50)

    @api.constrains('product_return_moves')
    def _check_quantity(self):
        if any(move.quantity < 0 for move in self.product_return_moves):
            raise ValidationError(_("Quantity cannot be negative"))
        if any(move.quantity > move.available_qty for move in self.product_return_moves):
            raise ValidationError(_("Quantity cannot be more than available quantity"))

    @api.model
    def default_get(self, fields):
        res = super(ReturnPicking, self).default_get(fields)

        if 'product_return_moves' in res:

            picking = self.env['stock.picking'].browse(self.env.context['active_id'])
            picking_returns = self.env['stock.picking'].search([
                ('origin', '=', picking.name),
                ('picking_type_id.code', '=', picking.picking_type_id.return_picking_type_id.code)])

            for move in res['product_return_moves']:
                # delivered qty
                qty_delivered = sum(picking.pack_operation_product_ids.filtered(
                    lambda operation: operation.product_id.id == move[2]['product_id']
                ).mapped('qty_done'))

                # returned qty of this DC
                qty_returned = sum(picking_returns.mapped('pack_operation_product_ids').filtered(
                    lambda operation: operation.product_id.id == move[2]['product_id']
                ).mapped('qty_done')) or 0.0

                # available qty for returning
                qty_available = qty_delivered - qty_returned

                if qty_available < move[2]['quantity']:
                    move[2]['quantity'] = qty_available

                move[2]['to_refund_so'] = True
                move[2]['available_qty'] = move[2]['quantity']

        return res

    @api.multi
    def _create_returns(self):
        picking = self.env['stock.picking'].browse(self.env.context['active_id'])

        pickings = self.env['stock.picking'].search([('origin', '=', picking.origin),
                                                     ('picking_type_id', '=', picking.picking_type_id.id),
                                                     ('state', 'in', ['partially_available', 'assigned'])])
        if pickings:
            raise UserError(
                _("Unreserve the DC of %s which is in 'Partially Avaliable' or 'Available' state") % picking.origin)

        new_picking_id, picking_type_id = super(ReturnPicking, self)._create_returns()

        new_picking = self.env['stock.picking'].browse(new_picking_id)

        if new_picking.picking_type_id.code == 'outgoing_return':

            for pack in new_picking.pack_operation_ids:
                if pack.product_qty > 0:
                    pack.write({'qty_done': pack.product_qty})

            new_picking.write({'date_done': picking.date_done})

            new_picking.do_transfer()
            new_picking.button_ac_approve()
            new_picking.button_approve()

            # reverse cogs entry
            move = self.env['account.move'].search([('id', '=', picking.cogs_move_id.id)])
            if move:
                self.do_cogs_reverse_accounting(new_picking, move, False)
            if not picking.cogs_move_id:
                self.do_cogs_reverse_accounting(new_picking, False, self.price_unit_text)
            # Create DC with return qty or Add return qty with existing DC
            existing_dc = self.env['stock.picking'].search([('origin', '=', picking.origin),
                                                            ('picking_type_id', '=', picking.picking_type_id.id),
                                                            ('state', '=', 'confirmed')])
            if existing_dc:
                existing_dc.move_lines[0].product_uom_qty += new_picking.pack_operation_product_ids[0].qty_done
            else:
                new_dc = picking.copy()
                new_dc.move_lines[0].product_uom_qty = new_picking.pack_operation_product_ids[0].qty_done
                new_dc.action_confirm()

        return new_picking_id, picking_type_id

    @api.multi
    def do_reverse_cogs_with_text_price_unit(self):
        ref = "reversal of: cogs"
        picking = self.env['stock.picking'].browse(self.env.context['active_id'])
        for line in self.product_return_moves:
            amount = self.price_unit_text * line.quantity
            label = line.product_id.display_name + "; Rate: " + str(self.price_unit_text) + "; Qty: " + str(
                line.quantity)

            credit_line_vals = {
                'name': label,
                'product_id': line.product_id.id,
                'product_uom_id': line.product_id.uom_id.id,
                'account_id': line.product_id.product_tmpl_id.raw_cogs_account_id.id,
                'quantity': line.quantity,
                'ref': ref,
                'partner_id': False,
                'debit': amount if amount > 0 else 0,
                'credit': -amount if amount < 0 else 0,
                'operating_unit_id': picking.operating_unit_id.id
            }

            debit_line_vals = {
                'name': label,
                'product_id': line.product_id.id,
                'product_uom_id': line.product_id.uom_id.id,
                'account_id': line.product_id.categ_id.property_stock_valuation_account_id.id,
                'quantity': line.quantity,
                'ref': ref,
                'partner_id': False,
                'credit': amount if amount > 0 else 0,
                'debit': -amount if amount < 0 else 0,
                'operating_unit_id': picking.operating_unit_id.id,
                'cost_center_id': line.product_id.product_tmpl_id.cost_center_id.id
            }
            move_lines = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]

            AccountMove = self.env['account.move']
            journal_id = line.product_id.categ_id.property_stock_journal.id

            # convert datetime to local time
            user_tz = self.env.user.tz or pytz.utc
            local = pytz.timezone(user_tz)
            dt = datetime.strftime(
                pytz.utc.localize(datetime.strptime(self.return_date, "%Y-%m-%d")).astimezone(local),
                "%Y-%m-%d %H:%M:%S")

            new_account_move = AccountMove.create({
                'journal_id': journal_id,
                'line_ids': move_lines,
                'date': dt,
                'operating_unit_id': picking.operating_unit_id.id,
                'ref': ref})

            return new_account_move

    def do_cogs_reverse_accounting(self, picking, move, price_unit_text):
        product = picking.pack_operation_product_ids[0].product_id
        stock_pack_operation = picking.pack_operation_product_ids[0]

        if price_unit_text:
            # no cogs entry
            move = self.do_reverse_cogs_with_text_price_unit()
            move.post()
        else:
            ref = "reversal of: " + move.name
            amount = self.price_unit * stock_pack_operation.qty_done
            name = product.display_name + "; Rate: " + str(self.price_unit) + "; Qty: " + str(
                stock_pack_operation.qty_done)

            move_of_reverse_cogs = move.copy(default={'ref': ref, 'date': self.return_date})
            for aml in move_of_reverse_cogs.line_ids:
                aml.date = self.return_date
                if aml.debit > 0:
                    aml.name = name
                    aml.debit = 0
                    aml.credit = amount
                else:
                    aml.name = name
                    aml.credit = 0
                    aml.debit = amount

            move_of_reverse_cogs.post()

    ################# NEW Implementation #################

    def do_operation(self, rec, picking, return_moves, pro_returns, main_invoice):
        new_picking_id, pick_type_id = rec._create_returns()
        partner_acc_rec = picking.partner_id.property_account_receivable_id.id
        sale_journal_id = self.env['account.journal'].search([('type', '=', 'sale'),
                                                              ('company_id', '=', picking.company_id.id)])[0]
        sale_order_obj = self.env['sale.order'].search([('name', '=', picking.origin)])[0]
        refund_obj = {
            'number': self.env['ir.sequence'].sudo().next_by_code('account.invoice'),
            'name': rec.return_reason,
            'partner_id': picking.partner_id.id,
            'date_invoice': rec.return_date,
            'currency_id': sale_order_obj.currency_id.id,
            'sale_type_id': sale_order_obj.type_id.id,
            'type': 'out_refund',
            'user_id': main_invoice.user_id.id,
            'operating_unit_id': picking.operating_unit_id.id,
            'journal_id': sale_journal_id.id,
            'company_id': picking.company_id.id,
            'account_id': partner_acc_rec,
            'so_id': sale_order_obj.id,
            'conversion_rate': main_invoice.conversion_rate,
            'cost_center_id': main_invoice.cost_center_id.id or False,
            'pack_type': main_invoice.pack_type.id or False,
            'lc_id': main_invoice.lc_id.id or False,
            'payment_term_id': main_invoice.payment_term_id.id or False,
            'origin': main_invoice.number,
            'refund_invoice_id': main_invoice.id
        }
        invoice_obj = self.env['account.invoice'].create(refund_obj)

        for move in return_moves:
            qty = 0
            for rtns in pro_returns:
                if rtns.move_id.id == move.id:
                    qty = rtns.quantity

            main_invoice_price_unit = self.get_main_invoice_price_unit(main_invoice.id, move.product_id.id)
            invoice_line = {
                'product_id': move.product_id.id,
                'name': move.product_id.name,
                'account_id': move.product_id.property_account_income_id.id,
                'quantity': qty,
                'uom_id': move.product_id.uom_id.id,
                'price_unit': main_invoice_price_unit,
                'invoice_id': invoice_obj.id,
                'cost_center_id': main_invoice.cost_center_id.id or False,
            }
            invoice_line_obj = self.env['account.invoice.line'].create(invoice_line)
        picking_obj = self.env['stock.picking'].browse(new_picking_id)
        picking_obj.write({'invoice_ids': [(4, invoice_obj.id)], 'date_done': rec.return_date})
        invoice_obj.sudo().action_invoice_open()

        # Reconciliation
        move_id = invoice_obj.move_id
        main_invoice_move = main_invoice.move_id
        info = self._get_outstanding_info(invoice_obj, main_invoice_move)
        self.assign_outstanding_credit(invoice_obj, info['content'][0]['id'])

        return True

    def get_main_invoice_price_unit(self, main_invoice_id, pro_id):
        invoice_line = self.env['account.invoice.line'].sudo().search(
            [('invoice_id', '=', main_invoice_id), ('product_id', '=', pro_id)], limit=1)
        return invoice_line.price_unit

    def _get_outstanding_info(self, invoice_obj, main_invoice_move):

        if invoice_obj.state == 'open':
            domain = [('account_id', '=', invoice_obj.account_id.id),
                      ('move_id', '=', main_invoice_move.id),
                      ('partner_id', '=', self.env['res.partner']._find_accounting_partner(invoice_obj.partner_id).id),
                      ('reconciled', '=', False),
                      '|',
                      '&', ('amount_residual_currency', '!=', 0.0), ('currency_id', '!=', None),
                      '&', ('amount_residual_currency', '=', 0.0), '&', ('currency_id', '=', None),
                      ('amount_residual', '!=', 0.0)]
            if invoice_obj.type in ('out_invoice', 'in_refund'):
                domain.extend([('credit', '>', 0), ('debit', '=', 0)])
                type_payment = _('Outstanding credits')
            else:
                domain.extend([('credit', '=', 0), ('debit', '>', 0)])
                type_payment = _('Outstanding debits')
            info = {'title': '', 'outstanding': True, 'content': [], 'invoice_id': invoice_obj.id}
            lines = self.env['account.move.line'].search(domain)
            currency_id = invoice_obj.currency_id
            if len(lines) != 0:
                for line in lines:
                    # get the outstanding residual value in invoice currency
                    if line.currency_id and line.currency_id == invoice_obj.currency_id:
                        amount_to_show = abs(line.amount_residual_currency)
                    else:
                        amount_to_show = line.company_id.currency_id.with_context(date=line.date).compute(
                            abs(line.amount_residual), invoice_obj.currency_id)
                    if float_is_zero(amount_to_show, precision_rounding=invoice_obj.currency_id.rounding):
                        continue
                    info['content'].append({
                        'journal_name': line.ref or line.move_id.name,
                        'amount': amount_to_show,
                        'currency': currency_id.symbol,
                        'id': line.id,
                        'position': currency_id.position,
                        'digits': [69, invoice_obj.currency_id.decimal_places],
                    })
                info['title'] = type_payment

            return info

    def assign_outstanding_credit(self, refund_invoice, credit_aml_id):
        credit_aml = self.env['account.move.line'].browse(credit_aml_id)
        if not credit_aml.currency_id and refund_invoice.currency_id != refund_invoice.company_id.currency_id:
            credit_aml.with_context(allow_amount_currency=True, check_move_validity=False).write({
                'amount_currency': refund_invoice.company_id.currency_id.with_context(date=credit_aml.date).compute(
                    credit_aml.balance, refund_invoice.currency_id),
                'currency_id': refund_invoice.currency_id.id})
        if credit_aml.payment_id:
            credit_aml.payment_id.write({'invoice_ids': [(4, refund_invoice.id, None)]})
        return refund_invoice.register_payment(credit_aml)

    @api.multi
    def create_return_obj(self):
        return_success = 0
        for rec in self:
            picking = self.env['stock.picking'].browse(self.env.context['active_id'])

            if not picking.origin:
                raise UserError(
                    _("Source Document not found for this picking! \n Source Document contains the reference of sale order!"))

            if not picking.partner_id.property_account_receivable_id:
                raise UserError(_("Receivable account not found for this customer!"))

            return_moves = self.product_return_moves.mapped('move_id')
            if not picking.invoice_ids:
                raise UserError(_("Invoice not found for this DC!"))
            else:
                for inv in picking.invoice_ids:
                    if inv.state == 'draft':
                        raise UserError(_("You need to validate the invoice. Invoice needs to be in open state!"))
                    elif inv.state == 'paid':
                        raise UserError(_("Invoice is already paid\n You need to unreconcile the invoice first!"))
                    elif inv.state == 'open':
                        return_operation = self.do_operation(rec, picking, return_moves, self.product_return_moves, inv)
                        if return_operation:
                            return_success = return_success + 1
                    else:
                        raise UserError(_("Invoice needs to be in open state!"))
        if return_success > 0:
            message_id = self.env['return.success.wizard'].create({'message': _(
                "Return Operation Successful!\nReverse COGS Entry Created Successfully.")
            })
            return {
                'name': _('Success'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'return.success.wizard',
                'context': {'picking_id': picking.id},
                'res_id': message_id.id,
                'target': 'new'
            }
