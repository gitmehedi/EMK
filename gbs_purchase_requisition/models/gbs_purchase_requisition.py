from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from datetime import date
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    _order = "requisition_date desc"

    name = fields.Char(string='Purchase Requisition',default='/')
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)

    region_type = fields.Selection([('local', 'Local'),('foreign', 'Foreign')],
                                   string="Region Type", help="Local: Local LC.\n""Foreign: Foreign LC.")

    purchase_by = fields.Selection([('cash', 'Cash'),
                                    ('credit', 'Credit'),
                                    ('lc', 'LC'),
                                    ('tt', 'TT')], string="Purchase By")

    purchase_from = fields.Selection([('own', 'Own'), ('ho', 'HO')],
                                   string="Purchase From")

    requisition_date = fields.Date(string='Requisition Date',required=True,default = date.today())
    required_date = fields.Date(string='Required Date')
    state = fields.Selection([('draft', 'Draft'), ('in_progress', 'Confirmed'),
                              ('approve_head_procurement', 'Waiting For Approval'),('done', 'Approved'),
                              ('cancel', 'Cancelled')],'Status', track_visibility='onchange', required=True,
                             copy=False, default='draft')

    indent_ids = fields.Many2many('indent.indent','pr_indent_rel','pr_id','indent_id',string='Indent')
    # attachment_ids = fields.Many2many('ir.attachment','attachment_pr_rel','pr_id','attachment_id', string='Attachments')
    attachment_ids = fields.One2many('ir.attachment','res_id', string='Attachments', domain=[('res_model', '=', 'purchase.requisition')])

    @api.multi
    def action_in_progress(self):
        if not all(obj.line_ids for obj in self):
            raise UserError(_('You cannot confirm call because there is no product line.'))
        res = {
            'state': 'in_progress'
        }
        requested_date = self.requisition_date
        new_seq = self.env['ir.sequence'].next_by_code_new('purchase.requisition',requested_date)

        if new_seq:
            res['name'] = new_seq

        self.write(res)

    @api.multi
    def action_open(self):
        res = self.env.ref('gbs_purchase_requisition.pr_from_where_wizard')
        result = {
            'name': _('Please take decision purchase from where?'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'pr.from.where.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result
        # self.write({'state': 'approve_head_procurement'})

    @api.multi
    def action_approve(self):
        res = self.env.ref('gbs_purchase_requisition.purchase_requisition_type_wizard')
        result = {
            'name': _('Please Select Region Type and Purchase By before approve'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'purchase.requisition.type.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result

    @api.onchange('indent_ids')
    def indent_product_line(self):
        vals = []
        # self.required_date = self.indent_ids.required_date
        for indent_id in self.indent_ids:
            indent_product_line_obj = self.env['indent.product.lines'].search([('indent_id','=',indent_id.id)])
            for indent_product_line in indent_product_line_obj:
                vals.append((0, 0, {'product_id': indent_product_line.product_id,
                                'name': indent_product_line.name,
                                'product_uom_id': indent_product_line.product_uom,
                                'product_ordered_qty': indent_product_line.product_uom_qty,
                                'product_qty': indent_product_line.qty_available,
                          }))
                self.line_ids = vals

    ####################################################
    # ORM Overrides methods
    ####################################################

    def unlink(self):
        for indent in self:
            if indent.state != 'draft':
                raise ValidationError(_('You cannot delete in this state'))
            else:
                query = """ delete from ir_attachment where res_id=%s"""
                for att in self.attachment_ids:
                    self._cr.execute(query, tuple([att.res_id]))
                return super(PurchaseRequisition, self).unlink()


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    product_ordered_qty = fields.Float('Ordered Quantities', digits=dp.get_precision('Product UoS'),
                                       default=1)
    name = fields.Char(related='product_id.name',string='Description',store=True)
    price_unit = fields.Float(related='product_id.standard_price',string='Unit Price', digits=dp.get_precision('Product Price'),store = True)
    product_uom_id = fields.Many2one(related='product_id.uom_id',comodel_name='product.uom', string='Product Unit of Measure',store=True)
    last_purchase_date = fields.Date(string='Last Purchase Date',compute = '_get_last_purchase',store = True)
    last_qty = fields.Float(string='Last Purchase Qnty',compute = '_get_last_purchase',store = True)
    last_product_uom_id = fields.Many2one('product.uom', string='Last Purchase Unit',compute = '_get_last_purchase',store=True)
    last_price_unit = fields.Float(string='Last Unit Price',compute = '_get_last_purchase',store = True)
    last_supplier_id = fields.Many2one(comodel_name='res.partner', string='Last Supplier', compute='_get_last_purchase',store=True)
    remark = fields.Char(string='Remarks')
    store_code = fields.Char(related='product_id.barcode',string='Store Code',size=20,store = True)

    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'),
                               compute='_get_product_quantity')


    @api.depends('product_id')
    @api.multi
    def _get_product_quantity(self):
        for product in self:

            location = self.env['stock.location'].search(
                [('operating_unit_id', '=', product.requisition_id.operating_unit_id.id), ('name', '=', 'Stock')])
            product_quant = self.env['stock.quant'].search([('product_id', '=', product.product_id.id),
                                                        ('location_id', '=', location.id)])
            quantity = sum([val.qty for val in product_quant])
            product.product_qty = quantity

    @api.onchange('product_id')
    def _onchange_product_id(self):
        pass

    @api.depends('product_id')
    @api.one
    def _get_last_purchase(self):
        """ Get last purchase price, last purchase date and last supplier """
        lines = self.env['purchase.order.line'].search(
            [('order_id.operating_unit_id','=',self.requisition_id.operating_unit_id.id),('product_id', '=', self.product_id.id),
             ('state', 'in', ['confirmed', 'purchase'])]).sorted(
            key=lambda l: l.order_id.date_order, reverse=True)
        self.last_purchase_date = lines[:1].order_id.date_order
        self.last_price_unit = lines[:1].price_unit
        self.last_supplier_id = lines[:1].order_id.partner_id.id
        self.last_qty = lines[:1].product_qty
        self.last_product_uom_id = lines[:1].product_uom.id