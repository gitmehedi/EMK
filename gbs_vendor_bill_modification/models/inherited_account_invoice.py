from odoo import _, api, fields, models
from lxml import etree
from odoo.exceptions import UserError, ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    is_after_automation = fields.Boolean()

    @api.onchange('pickings')
    def _onchange_pickings(self):
        if self.is_after_automation:
            if self.pickings:
                vals = []
                for picking in self.pickings:
                    for move in picking.move_lines:
                        if move.available_qty:
                            aval_qty = move.available_qty
                        else:
                            aval_qty = 0
                        found_product = 0
                        for val in vals:
                            if val[2]['product_id'] == move.product_id.id:
                                existing_qty = val[2]['quantity']
                                val[2]['quantity'] = existing_qty + aval_qty
                                val[2]['duplc_qty'] = existing_qty + aval_qty
                                found_product = found_product + 1
                                val[2]['move_ref'] = val[2]['move_ref'] + "," + "(" + str(move.id) + ":" + str(
                                    aval_qty) + ")"

                        if found_product == 0:
                            if not picking.origin:
                                raise UserError(_(
                                    'Origin of the related picking not found!\n Picking origin is where PO number or PO LC number saved!'
                                ))
                            lc = self.env['letter.credit'].search([('name', '=', picking.origin)])
                            po_obj = self.env['purchase.order'].search(
                                ['|', ('name', '=', picking.origin), ('po_lc_id', '=', lc.id)])
                            order_line = self.env['purchase.order.line'].search(
                                [('order_id', '=', po_obj.id), ('product_id', '=', move.product_id.id)],
                                limit=1)
                            analytic_account_id = False
                            if po_obj.region_type == 'foreign' or po_obj.is_service_order:
                                if po_obj.lc_ids:
                                    analytic_account_id = po_obj.lc_ids[0].analytic_account_id.id
                            elif po_obj.cnf_quotation:
                                analytic_account_id = po_obj.shipment_id.lc_id.analytic_account_id.id
                            if po_obj.region_type == 'foreign':
                                if not self.env.user.company_id.lc_pad_account:
                                    raise UserError(
                                        _("LC Goods In Transit Account not set. Please contact your system administrator for "
                                          "assistance."))
                                else:
                                    analytic_account_id = self.env.user.company_id.lc_pad_account.id

                            if float("{:.4f}".format(aval_qty)) != 0:
                                move_ref = "(" + str(move.id) + ":" + str(aval_qty) + ")"

                                vals.append((0, 0, {'product_id': move.product_id.id,
                                                    'quantity': aval_qty,
                                                    'duplc_qty': aval_qty,
                                                    'price_unit': move.price_unit,
                                                    'name': move.product_id.name,
                                                    'uom_id': move.product_uom.id,
                                                    'purchase_line_id': order_line.id,
                                                    'analytic_account_id': analytic_account_id,
                                                    'account_id': move.product_id.property_account_expense_id.id or move.product_id.categ_id.property_account_expense_categ_id.id,
                                                    'move_ref': move_ref
                                                    }))

                self.invoice_line_ids = vals
            else:
                self.invoice_line_ids = []

    def get_domain(self):
        pickings = self.env.context.get('default_pickings')
        if pickings:
            domain = [("id", "in", pickings)]
        else:
            domain = [('id', '=', -1)]
        return domain

    pickings = fields.Many2many(
        comodel_name='stock.picking',
        relation='invoice_picking_rel', column1='invoice_id',
        column2='picking_id', string='''MRR's''', domain=get_domain,
        help="Removing and Adding MRR option available only when your are creating a fresh vendor bill.\n  If you want to remove or add MRR  after saving the bill, you have to first cancel the existing bill then again try to create vendor bill by selecting MRRs"
    )

    from_po_form = fields.Boolean(default=False)

    @api.depends('partner_id')
    def _compute_direct_vendor_bill(self):
        default_direct_vendor_bill = self.env.context.get('default_direct_vendor_bill')
        if default_direct_vendor_bill:
            self.direct_vendor_bill = True
        else:
            self.direct_vendor_bill = False

    direct_vendor_bill = fields.Boolean(compute='_compute_direct_vendor_bill')

    def _prepare_invoice_line_from_po_line(self, line):
        """ Override parent's method to add lc analytic account on invoice line"""
        invoice_line = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        from_po_form = self.env.context.get('default_from_po_form')
        order_line = self.env['purchase.order.line'].browse(invoice_line['purchase_line_id'])
        product = self.env['purchase.order.line'].browse(invoice_line['product_id'])
        order_id = order_line.order_id
        lc_number = order_line.order_id.po_lc_id.name
        if self.type == 'in_invoice' and not order_id.is_service_order and not order_id.cnf_quotation:
            if order_line and product:
                mrr_qty = self.env['account.invoice.utility'].get_mrr_qty(order_id, lc_number, product)
                available_qty = self.env['account.invoice.utility'].get_available_qty(order_id, product.id, mrr_qty)
                # if available_qty  is 0 then don't load
                if available_qty <= 0:
                    return False

                invoice_line.update({'quantity': available_qty, 'duplc_qty': available_qty})

        return invoice_line

    # replacing odoo original method
    @api.onchange('purchase_id')
    def purchase_order_change(self):
        # res = super(AccountInvoice, self).purchase_order_change()
        if not self.purchase_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.purchase_id.partner_id.id

        if self.partner_id.id != self.purchase_id.partner_id.id:
            raise UserError(_(
                'You need select purchase order of the selected vendor!'
            ))

        new_lines = self.env['account.invoice.line']
        for line in self.purchase_id.order_line - self.invoice_line_ids.mapped('purchase_line_id'):
            data = self._prepare_invoice_line_from_po_line(line)
            if data:
                if data['quantity'] > 0 and data['price_unit'] > 0:
                    new_line = new_lines.new(data)
                    new_line._set_additional_fields(self)
                    new_lines += new_line

        # all not cancelled invoice for this order
        order_lines = self.env['purchase.order.line'].search([('order_id', '=', self.purchase_id.id)])
        invoice_lines = self.env['account.invoice.line'].search(
            [('purchase_line_id', 'in', order_lines.ids)])
        total_invoiced = 0
        for line in invoice_lines:
            if line.invoice_id.state != 'cancel':
                total_invoiced = total_invoiced + line.quantity

        total_invoiced = float("{:.4f}".format(total_invoiced))

        pickings = self.env['stock.picking'].search(
            ['|', ('origin', '=', self.purchase_id.name), ('origin', '=', self.purchase_id.po_lc_id.name),
             ('check_mrr_button', '=', True)])

        moves = self.env['stock.move'].search(
            [('picking_id', 'in', pickings.ids), ('state', '=', 'done')])
        total_mrr_qty = float("{:.4f}".format(sum(move.product_qty for move in moves)))
        if total_invoiced != 0 and total_mrr_qty != 0 and total_invoiced >= total_mrr_qty:
            raise UserError(_('All MRR has been billed for this order!'))

        if self.env.user.company_id.mrr_bill_automation_date < self.purchase_id.date_order and not self.purchase_id.is_service_order and not self.purchase_id.cnf_quotation:
            pickings_ids = []
            for picking in pickings:
                moves = self.env['stock.move'].search(
                    [('picking_id', 'in', picking.ids), ('state', '=', 'done')])
                for move in moves:
                    if float("{:.4f}".format(move.available_qty)) != 0:
                        if picking.id not in pickings_ids:
                            pickings_ids.append(picking.id)
            if self.pickings:
                for pick in self.pickings:
                    pickings_ids.append(pick.id)

            self.pickings = [(6, 0, pickings_ids)]
            self.is_after_automation = True
        else:
            self.pickings += pickings
        self.invoice_line_ids += new_lines
        self.purchase_id = False

        return {}

    @api.constrains('invoice_line_ids')
    def _check_qty_price(self):
        for rec in self:
            if len(rec.invoice_line_ids) > 0:
                for line in rec.invoice_line_ids:
                    if line.quantity <= 0:
                        raise ValidationError("Line Quantity cannot be 0!")
                    if line.price_unit <= 0:
                        raise ValidationError("Line Unit Price cannot be 0!")

    # overriden odoo method
    @api.onchange('state', 'partner_id', 'invoice_line_ids')
    def _onchange_allowed_purchase_ids(self):
        result = {}
        # A PO can be selected only if at least one PO line is not already in the invoice
        purchase_line_ids = self.invoice_line_ids.mapped('purchase_line_id')
        purchase_ids = self.invoice_line_ids.mapped('purchase_id').filtered(lambda r: r.order_line <= purchase_line_ids)

        domain = [('invoice_status', 'in', ('to invoice', 'invoiced'))]
        if self.partner_id:
            domain += [('partner_id', 'child_of', self.partner_id.id)]
        if purchase_ids:
            domain += [('id', 'not in', purchase_ids.ids)]
        result['domain'] = {'purchase_id': domain}
        return result
