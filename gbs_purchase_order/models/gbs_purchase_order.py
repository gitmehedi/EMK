# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError
import odoo.addons.decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _default_picking_type(self):
        type_obj = self.env['stock.picking.type']
        company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
        if not types:
            types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id', '=', False)])
        return types[:1]

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    @api.depends('order_line.price_total','amount_discount')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                if order.company_id.tax_calculation_rounding_method == 'round_globally':
                    taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty,
                                                      product=line.product_id, partner=line.order_id.partner_id)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax

            amount_after_discount = amount_untaxed + amount_tax - order.amount_discount
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_after_tax': amount_untaxed + amount_tax,
                'amount_after_discount': amount_after_discount,
                'amount_total': amount_untaxed + amount_tax - order.amount_discount
            })

    name = fields.Char('Order Reference', required=True, index=True, copy=False, default='New', track_visibility='onchange')
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)
    region_type = fields.Selection([('local', 'Local'), ('foreign', 'Foreign')], string="Region Type",
                                   help="Local: Local LC.\n""Foreign: Foreign LC.")
    purchase_by = fields.Selection([('cash', 'Cash'), ('credit', 'Credit'), ('lc', 'LC'), ('tt', 'TT')],
                                   string="Purchase By")
    attachment_ids = fields.One2many('ir.attachment','res_id', string='Attachments', domain=[('res_model', '=', 'purchase.order')])
    check_po_action_button = fields.Boolean('Check PO Action Button', default=False)
    disable_new_revision_button = fields.Boolean('Disable New Revision Button', default=False)

    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To', states=READONLY_STATES, required=True,
                                      default=_default_picking_type,
                                      help="This will determine picking type of incoming shipment")
    default_location_dest_id_usage = fields.Selection(related='picking_type_id.default_location_dest_id.usage',
                                                      string='Destination Location Type',
                                                      related_sudo=True,
                                                      help="Technical field used to display the Drop Ship Address",
                                                      readonly=True)

    # contact_person = fields.Many2many('res.partner','partner_po_rel','po_id','partner_id','Contact Person')
    contact_person_txt = fields.Char('Contact Person')

    ref_date = fields.Date('Ref.Date')

    currency_id = fields.Many2one(related='partner_id.property_purchase_currency_id',required=True, store=True,
                                  string='Currency', readonly=True)

    # currency_id = fields.Many2one('res.currency', 'Currency', required=True, readonly=True,
    #                               default=lambda self: self.partner_id.currency_id.id)

    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')

    amount_tax = fields.Monetary(string='VAT', store=True, readonly=True, compute='_amount_all')
    amount_vat = fields.Float(string='TDS(%)')
    is_tds_applicable = fields.Boolean(string='TDS Applicable', default=False)


    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')

    amount_discount = fields.Float(string='Write-off')
    amount_after_tax = fields.Monetary(string='After VAT', store=True, readonly=True, compute='_amount_all')
    amount_after_discount = fields.Monetary(string='After Write-off', store=True, readonly=True,compute='_amount_all')
    amount_after_vat = fields.Monetary(string='After TAX', store=True, readonly=True,compute='_amount_all')
    terms_condition = fields.Text(string='Terms & Conditions', readonly=True,
                                  states={'draft': [('readonly', False)]})


    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        if not self.requisition_id:
            return

        due_products = self.requisition_id.line_ids.filtered(lambda x: x.product_ordered_qty - x.receive_qty > 0)
        if not due_products:
            raise UserError('No due so no quotation required!!!')
        else:
            requisition = self.requisition_id
            if self.partner_id:
                partner = self.partner_id
            else:
                partner = requisition.vendor_id
            payment_term = partner.property_supplier_payment_term_id
            currency = partner.property_purchase_currency_id or requisition.company_id.currency_id

            FiscalPosition = self.env['account.fiscal.position']
            fpos = FiscalPosition.get_fiscal_position(partner.id)
            fpos = FiscalPosition.browse(fpos)

            self.partner_id = partner.id
            self.fiscal_position_id = fpos.id
            self.payment_term_id = payment_term.id,
            self.company_id = requisition.company_id.id
            self.currency_id = currency.id
            self.origin = requisition.name
            self.partner_ref = requisition.name  # to control vendor bill based on agreement reference
            self.notes = requisition.description
            self.date_order = requisition.date_end or fields.Datetime.now()
            self.picking_type_id = requisition.picking_type_id.id
            self.operating_unit_id = requisition.operating_unit_id

            if requisition.type_id.line_copy != 'copy':
                return

            # Create PO lines if necessary
            order_lines = []
            for line in due_products:
                # Compute name
                product_lang = line.product_id.with_context({
                    'lang': partner.lang,
                    'partner_id': partner.id,
                })
                name = product_lang.display_name
                if product_lang.description_purchase:
                    name += '\n' + product_lang.description_purchase

                # Compute taxes
                if fpos:
                    taxes_ids = fpos.map_tax(line.product_id.supplier_taxes_id.filtered(
                        lambda tax: tax.company_id == requisition.company_id)).ids
                else:
                    taxes_ids = line.product_id.supplier_taxes_id.filtered(
                        lambda tax: tax.company_id == requisition.company_id).ids

                # Compute quantity and price_unit
                if line.product_uom_id != line.product_id.uom_po_id:
                    product_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_po_id)
                    price_unit = line.product_uom_id._compute_price(line.price_unit, line.product_id.uom_po_id)
                else:
                    product_qty = line.product_qty
                    price_unit = line.price_unit

                if requisition.type_id.quantity_copy != 'copy':
                    product_qty = 0

                # Compute price_unit in appropriate currency
                if requisition.company_id.currency_id != currency:
                    price_unit = requisition.company_id.currency_id.compute(price_unit, currency)

                # Create PO line
                order_lines.append((0, 0, {
                    'name': line.name,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_id.uom_po_id.id,
                    'product_qty': line.product_ordered_qty - line.receive_qty,
                    'price_unit': price_unit,
                    'taxes_id': '',
                    'date_planned': requisition.schedule_date or fields.Date.today(),
                    'procurement_ids': [(6, 0, [requisition.procurement_id.id])] if requisition.procurement_id else False,
                    'account_analytic_id': line.account_analytic_id.id,
                }))
            self.order_line = order_lines
            if requisition.attachment_ids:
                attachments_lines = []
                for attachment_line in requisition.attachment_ids:
                    attachments_lines.append((0, 0, {
                        'name': attachment_line.name,
                        'datas_fname': attachment_line.datas_fname,
                        'db_datas': attachment_line.db_datas,
                        'res_model': 'purchase.order',
                    }))
                self.attachment_ids = attachments_lines

            if requisition.region_type:
                self.region_type = requisition.region_type
            if requisition.purchase_by:
                self.purchase_by = requisition.purchase_by
            if requisition.state == 'done':
                self.check_po_action_button = True

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        if self.picking_type_id.sudo().default_location_dest_id.usage != 'customer':
            self.dest_address_id = False

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        type_obj = self.env['stock.picking.type']
        if self.operating_unit_id:
            types = type_obj.search([('code', '=', 'incoming'),
                                     ('operating_unit_id', '=',self.operating_unit_id.id)])
            if types:
                self.picking_type_id = types[0]
            else:
                raise UserError(
                    _("No Warehouse found with the Operating Unit indicated "
                      "in the Purchase Order")
                )

    @api.model
    def _default_picking_type(self):
        res = super(PurchaseOrder, self)._default_picking_type()
        type_obj = self.env['stock.picking.type']
        if self.operating_unit_id:
            types = type_obj.search([('code', '=', 'incoming'),
                                 ('operating_unit_id', '=',self.operating_unit_id.id)])
            if types:
                res = types[0].id
            else:
                res = False
        return res

    @api.multi
    def button_confirm(self):
        # res = {}
        res_wizard_view = self.env.ref('gbs_purchase_order.purchase_order_type_wizard')
        res = {
            'name': _('Please Select LC Region Type and Purchase By before approve'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res_wizard_view and res_wizard_view.id or False,
            'res_model': 'purchase.order.type.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'context': {'region_type': self.region_type or False,
                        'purchase_by': self.purchase_by or False},
            'target': 'new',
        }

        # res['return_original_method'] = super(PurchaseOrder, self).button_confirm()
        return res

    @api.multi
    def button_cancel(self):
        res = super(PurchaseOrder, self).button_cancel()
        for i in self:
            i.check_po_action_button = False
        return res

    @api.multi
    def new_revision(self):
        res = super(PurchaseOrder, self).new_revision()
        if self.requisition_id.state == 'done':
            self.check_po_action_button = True
        else:
            self.check_po_action_button = False
        return res

    @api.multi
    def action_update(self):
        for order in self:
            if order.requisition_id:
                for line in order.order_line:
                    pr_line_id = order.requisition_id.line_ids.filtered(lambda x: x.product_id.id == line.product_id.id)
                    if pr_line_id:
                        pr_line_id[0].write({'receive_qty': pr_line_id[0].receive_qty + line.product_qty})
                        self._cr.execute('INSERT INTO po_pr_line_rel (pr_line_id,po_line_id) VALUES (%s, %s)',
                                 tuple([pr_line_id[0].id, line.id]))

    ####################################################
    # ORM Overrides methods
    ####################################################

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            requested_date = datetime.strptime(vals['date_order'], "%Y-%m-%d %H:%M:%S").date()
            op_unit_obj = self.env['operating.unit'].search([('id', '=', vals['operating_unit_id'])])
            vals['name'] = self.env['ir.sequence'].next_by_code_new('purchase.quotation',requested_date,op_unit_obj) or '/'
        if not vals.get('requisition_id'):
            vals['check_po_action_button'] = True
        partner_currency_id = self.env['res.partner'].search([('id', '=', vals['partner_id'])]).property_purchase_currency_id
        if not partner_currency_id:
            raise UserError(_('Currency not set for this Supplier. Please at first set the currency'))
        return super(PurchaseOrder, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('requisition_id'):
            vals['check_po_action_button'] = False
        res = super(PurchaseOrder, self).write(vals)
        return res

    def unlink(self):
        for obj in self:
            if obj.state != 'cancel':
                raise ValidationError(_('You cannot delete in this state'))
            else:
                query = """ delete from attachment_po_rel where po_id=%s"""
                for att in obj.attachment_ids:
                    self._cr.execute(query, tuple([att.res_id]))
                return super(PurchaseOrder, self).unlink()


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # relation between PO line and PR line----------------------------------------
    pr_line_ids = fields.Many2many('purchase.requisition.line', 'po_pr_line_rel', 'po_line_id', 'pr_line_id',
                                       string='Purchase Requisition Lines')
    product_uom_view = fields.Many2one('product.uom',related='product_id.uom_id', string='Product Unit of Measure',
                                       store=True,readonly=True)

    # qty_invoiced = fields.Float(compute='_compute_qty_invoiced', string="Billed Qty",
    #                             digits=dp.get_precision('Product Unit of Measure'), store=True)
    # qty_received = fields.Float(compute='_compute_qty_received', string="Received Qty",
    #                             digits=dp.get_precision('Product Unit of Measure'), store=True)