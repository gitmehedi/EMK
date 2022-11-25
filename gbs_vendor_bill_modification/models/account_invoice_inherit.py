from odoo import _, api, fields, models
from lxml import etree
from odoo.exceptions import UserError, ValidationError
import re


class AccountInvoiceInherit(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def create(self, vals):
        order_id = self.env.context.get('purchase_order')
        type = self.env.context.get('invoice_type')
        default_type = self.env.context.get('default_type')
        purchase_order_obj = self.env['purchase.order'].browse(order_id)
        if type == 'in_invoice' or default_type == 'in_invoice' and not purchase_order_obj.cnf_quotation and not purchase_order_obj.is_service_order:
            if 'invoice_line_ids' in vals:
                if not vals['invoice_line_ids']:
                    raise UserError(
                        _('Invoice lines cannot be empty!'))
                else:
                    # update selected pickings available quantity
                    pickings_len = 0
                    if 'pickings' in vals:
                        pickings_len = len(vals['pickings'][0][2])
                        selected_pickings = vals['pickings'][0][2]
                        for picking_id in selected_pickings:
                            stock_move = self.env['stock.move'].search([('picking_id', '=', picking_id)])
                            for move in stock_move:
                                move.sudo().write({'available_qty': 0.0})
                            picking_obj = self.env['stock.picking'].browse(picking_id)
                            picking_obj.sudo().write({'mrr_status': 'full_billed'})

                    # if line quantity change update available quantity
                    for line in vals['invoice_line_ids']:
                        if line[2]['duplc_qty'] != line[2]['quantity']:
                            if pickings_len != 1:
                                raise UserError(
                                    _('You have to select only one MRR when editing the quantity!'))

                            qty_diff = line[2]['duplc_qty'] - line[2]['quantity']
                            if qty_diff < 0:
                                raise UserError(
                                    _('You cannot edit to increase quantity of a product!'))
                            # this qty_diff should be available for selected picking
                            if 'pickings' in vals:
                                selected_pickings = vals['pickings'][0][2]
                                for picking_id in selected_pickings:
                                    stock_move = self.env['stock.move'].search(
                                        [('picking_id', '=', picking_id), ('product_id', '=', line[2]['product_id'])])
                                    updated_qty = float("{:.4f}".format(qty_diff))
                                    for move in stock_move:
                                        move.sudo().write({'available_qty': updated_qty})
                                    picking_obj = self.env['stock.picking'].browse(picking_id)
                                    picking_obj.sudo().write({'mrr_status': 'partial_billed'})
            else:
                raise UserError(
                    _('Invoice lines cannot be empty!'))
        return super(AccountInvoiceInherit, self).create(vals)

    @api.multi
    def write(self, values):

        if self.invoice_line_ids and self.type == 'in_invoice':
            if not self.purchase_id.cnf_quotation and not self.purchase_id.is_service_order:
                if 'pickings' in values:
                    after_edit_selected_pickings = values['pickings'][0][2]
                    before_edit_selected_pickings = self.pickings.ids
                    removed_pickings = list(set(before_edit_selected_pickings).difference(after_edit_selected_pickings))

                    if removed_pickings:
                        raise UserError(
                            _('You cannot remove or add mrr in edit mode!\n Special note : You need to cancel this bill, then create a fresh bill by selecting MRRs'))

                if 'invoice_line_ids' in values:
                    for line in values['invoice_line_ids']:
                        invoice_line_obj = self.env['account.invoice.line'].browse(line[1])
                        if line[2]:
                            if invoice_line_obj and 'quantity' in line[2] and line[2]['quantity'] != invoice_line_obj.quantity:
                                picking_len = len(self.pickings)
                                if picking_len != 1:
                                    raise UserError(
                                        _('You have to select only one MRR when editing the quantity!\n Special note : If you cannot keep one MRR selected then you need to cancel this bill, then create a fresh bill by selecting MRRs'))
                                if float("{:.4f}".format(invoice_line_obj.quantity)) < float("{:.4f}".format(line[2]['quantity'])):
                                    raise UserError(_('You cannot edit increase previous quantity'))
                                diff_qty = float("{:.4f}".format(invoice_line_obj.quantity - line[2]['quantity']))

                                move_refs = invoice_line_obj.move_ref.split(',')
                                used = 0
                                for mr in move_refs:
                                    x = mr.split(':')
                                    move_id = x[0][1:]
                                    used_qty = x[1][:-1]
                                    qty = float(used_qty)
                                    if diff_qty <= float(used_qty) and used == 0:
                                        qty = float(used_qty) - float("{:.4f}".format(line[2]['quantity']))
                                        used = used + 1
                                    stock_move = self.env['stock.move'].browse(int(move_id))
                                    stock_move.sudo().write(
                                        {'available_qty': stock_move.available_qty + qty})
                                # for picking in self.pickings:
                                #     stock_move_obj = self.env['stock.move'].search(
                                #         [('product_id', '=', invoice_line_obj.product_id.id),
                                #          ('picking_id', '=', picking.id)])
                                #     for move in stock_move_obj:
                                #         if float("{:.4f}".format(invoice_line_obj.quantity)) < float(
                                #                 "{:.4f}".format(line[2]['quantity'])):
                                #             raise UserError(_('You cannot edit increase previous quantity'))
                                #         available_qty = float(
                                #             "{:.4f}".format(invoice_line_obj.quantity - line[2]['quantity']))
                                #         move.sudo().write(
                                #             {'available_qty': available_qty})
                                #     picking.sudo().write({'mrr_status': 'partial_billed'})

        res = super(AccountInvoiceInherit, self).write(values)
        return res

    @api.multi
    def action_invoice_cancel(self):
        # TODO : edited quantity not mentioned
        res = super(AccountInvoiceInherit, self).action_invoice_cancel()
        if self.invoice_line_ids and self.type == 'in_invoice' and self.is_after_automation:
            if not self.purchase_id.cnf_quotation and not self.purchase_id.is_service_order:
                for line in self.invoice_line_ids:
                    move_refs = line.move_ref.split(',')
                    for mr in move_refs:
                        x = mr.split(':')
                        move_id = x[0][1:]
                        used_qty = float(x[1][:-1])
                        stock_move = self.env['stock.move'].browse(int(move_id))
                        stock_move.sudo().write(
                            {'available_qty': stock_move.available_qty + float(used_qty)})
        return res

    @api.multi
    def action_invoice_draft(self):
        # TODO : edited quantity not mentioned write method workd
        res = super(AccountInvoiceInherit, self).action_invoice_draft()
        if self.invoice_line_ids and self.type == 'in_invoice' and self.is_after_automation:
            if not self.purchase_id.cnf_quotation and not self.purchase_id.is_service_order:
                for line in self.invoice_line_ids:
                    move_refs = line.move_ref.split(',')
                    for mr in move_refs:
                        x = mr.split(':')
                        move_id = x[0][1:]
                        used_qty = float(x[1][:-1])
                        stock_move = self.env['stock.move'].browse(int(move_id))
                        if float("{:.4f}".format(stock_move.available_qty)) - float("{:.4f}".format(used_qty)) < 0:
                            raise UserError(
                                _('This bill cannot be reset to draft!\n Fresh Bill may have create using selected MRR quantity!'))

                        stock_move.sudo().write(
                            {'available_qty': stock_move.available_qty - float(used_qty)})

        return res

    @api.multi
    def unlink(self):
        res = super(AccountInvoiceInherit, self).unlink()
        if self.invoice_line_ids and self.type == 'in_invoice' and self.is_after_automation:
            if not self.purchase_id.cnf_quotation and not self.purchase_id.is_service_order:
                for line in self.invoice_line_ids:
                    for line in self.invoice_line_ids:
                        move_refs = line.move_ref.split(',')
                        for mr in move_refs:
                            x = mr.split(':')
                            move_id = x[0][1:]
                            used_qty = float(x[1][:-1])
                            stock_move = self.env['stock.move'].browse(int(move_id))
                            stock_move.sudo().write(
                                {'available_qty': stock_move.available_qty + float(used_qty)})
        return res

    @api.multi
    def open_wizard_cancel(self, context=None):
        return {
            'name': ('Add Reason'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'add.invoice.reason',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new'
        }
