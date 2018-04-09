# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    name = fields.Char('Order Reference', required=True, index=True, copy=False, default='New')
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)
    region_type = fields.Selection([('local', 'Local'), ('foreign', 'Foreign')], string="Region Type",
                                   help="Local: Local LC.\n""Foreign: Foreign LC.")
    purchase_by = fields.Selection([('cash', 'Cash'), ('credit', 'Credit'), ('lc', 'LC'), ('tt', 'TT')],
                                   string="Purchase By")
    attachment_ids = fields.One2many('ir.attachment', 'res_id', string='Attachments')
    check_po_action_button = fields.Boolean('Check PO Action Button', default=False)
    disable_new_revision_button = fields.Boolean('Disable New Revision Button', default=False)

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        if not self.requisition_id:
            return

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

        if requisition.type_id.line_copy != 'copy':
            return

        # Create PO lines if necessary
        order_lines = []
        for line in requisition.line_ids:
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
                'product_qty': line.product_ordered_qty,
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
                }))
            self.attachment_ids = attachments_lines
        if requisition.region_type:
            self.region_type = requisition.region_type
        if requisition.purchase_by:
            self.purchase_by = requisition.purchase_by
        if requisition.state == 'done':
            self.check_po_action_button = True

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

    ####################################################
    # ORM Overrides methods
    ####################################################

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            requested_date = datetime.strptime(vals['date_order'], "%Y-%m-%d %H:%M:%S").date()
            vals['name'] = self.env['ir.sequence'].next_by_code_new('purchase.quotation',requested_date) or '/'
        if not vals.get('requisition_id'):
            vals['check_po_action_button'] = True
        return super(PurchaseOrder, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('requisition_id'):
            vals['check_po_action_button'] = False
        res = super(PurchaseOrder, self).write(vals)
        return res

    def unlink(self):
        for indent in self:
            if indent.state != 'draft':
                raise ValidationError(_('You cannot delete in this state'))
            else:
                query = """ delete from ir_attachment where res_id=%s"""
                for att in self.attachment_ids:
                    self._cr.execute(query, tuple([att.res_id]))
                return super(PurchaseOrder, self).unlink()
