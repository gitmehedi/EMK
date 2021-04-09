from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


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

    requisition_date = fields.Date(string='Requisition Date',required=True, default=lambda self: fields.datetime.now())
    required_date = fields.Date(string='Required Date')
    state = fields.Selection([('draft', 'Draft'), ('in_progress', 'Confirmed'),
                              ('approve_head_procurement', 'Waiting For Approval'),('done', 'Approved'),('close','Done'),
                              ('cancel', 'Cancelled')],'Status', track_visibility='onchange', required=True,
                             copy=False, default='draft')

    indent_ids = fields.Many2many('indent.indent','pr_indent_rel','pr_id','indent_id',string='Indent')
    # attachment_ids = fields.Many2many('ir.attachment','attachment_pr_rel','pr_id','attachment_id', string='Attachments')
    attachment_ids = fields.One2many('ir.attachment','res_id', string='Attachments', domain=[('res_model', '=', 'purchase.requisition')])

    dept_location_id = fields.Many2one('stock.location', string='Department', readonly=True,
                                       states={'draft': [('readonly', False)]},
                                       help="Default User Departmental Location.",
                                       default=lambda self: self.env.user.default_location_id)

    @api.onchange('user_id')
    def onchange_user_id(self):
        if self.user_id:
            return {'domain': {
                'dept_location_id': [('id', 'in', self.user_id.location_ids.ids), ('can_request', '=', True)]}}

    @api.one
    def action_done(self):
        if self.sudo().env.user.has_group(
                'gbs_procure_n_commercial_access.group_pr_done'):
            self.suspend_security().write({'state': 'close'})
        else:
            self.write({'state': 'close'})


    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_back_to_approve(self):
        if self.sudo().env.user.has_group(
                'commercial.group_commercial_manager'):
            self.suspend_security().write({'state': 'done'})
        else:
            self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):

        if self.sudo().env.user.has_group(
                'commercial.group_commercial_manager'):
            self.suspend_security().write({'state': 'cancel'})
        else:
            self.write({'state': 'cancel'})

    @api.multi
    def action_in_progress(self):
        if not all(obj.line_ids for obj in self):
            raise UserError(_('You cannot confirm call because there is no product line.'))
        res = {
            'state': 'in_progress'
        }
        requested_date = self.requisition_date
        operating_unit = self.operating_unit_id
        new_seq = self.env['ir.sequence'].next_by_code_new('purchase.requisition',requested_date,operating_unit)

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
    def action_get_indent(self):
        action = self.env.ref('gbs_purchase_requisition.action_pr_stock_indent').read([])[0]
        action['domain'] = [('id', '=', self.indent_ids.ids)]
        return action

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
            'context': {'default_region_type': self.region_type, 'default_purchase_by': self.purchase_by},
            'target': 'new',
        }
        return result

    @api.onchange('indent_ids')
    def indent_product_line(self):
        vals = []
        # self.required_date = self.indent_ids.required_date
        if self.indent_ids:
            for indent_id in self.indent_ids:
                if not self.dept_location_id:
                    self.dept_location_id = indent_id.stock_location_id.id
                elif self.dept_location_id.id != indent_id.stock_location_id.id:
                    raise UserError(_('Indent department and PR department must be same.'))
                indent_product_line_obj = self.env['indent.product.lines'].search([('indent_id','=',indent_id.id)])
                for indent_product_line in indent_product_line_obj:
                    vals.append((0, 0, {'product_id': indent_product_line.product_id,
                                    'name': indent_product_line.name,
                                    'product_uom_id': indent_product_line.product_uom,
                                    'product_ordered_qty': indent_product_line.product_uom_qty,
                                    'product_qty': indent_product_line.qty_available,
                              }))
                    self.line_ids = vals
        else:
            self.line_ids = []

    ####################################################
    # ORM Overrides methods
    ####################################################

    @api.multi
    def unlink(self):
        for indent in self:
            if indent.state != 'draft':
                raise ValidationError(_('You cannot delete in this state'))
            else:
                query = """ delete from ir_attachment where res_id=%s"""
                for att in indent.attachment_ids:
                    self._cr.execute(query, tuple([att.res_id]))
                return super(PurchaseRequisition, self).unlink()

    @api.constrains('line_ids')
    def _validation_line_ids(self):
        product_id_list = [line.product_id.id for line in self.line_ids]
        if len(product_id_list) != len(set(product_id_list)):
            raise ValidationError(_("Duplicate product found in products line."))


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    product_ordered_qty = fields.Float('Ordered Qty', digits=dp.get_precision('Product UoS'),
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
    store_code = fields.Char(related='product_id.default_code',readonly=True,string='Store Code',size=20,store = True)

    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'),
                               compute='_get_product_quantity')

    receive_qty = fields.Float(string='PO Qty')
    due_qty = fields.Float(string='Due Qty',compute='_compute_due_qty')

    @api.depends('product_ordered_qty', 'receive_qty')
    def _compute_due_qty(self):
        for line in self:
            if line.product_ordered_qty and line.receive_qty:
                diff = line.product_ordered_qty - line.receive_qty
                if diff>0:
                    line.due_qty = diff
                else:
                    line.due_qty = 0.0
            else:
                line.due_qty = line.product_ordered_qty


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

    @api.depends('product_id')
    @api.one
    def _get_last_purchase(self):
        """ Get last purchase price, last purchase date and last supplier """
        if self.product_id:
            lines = self.env['purchase.order.line'].search(
                [('order_id.operating_unit_id','=',self.requisition_id.operating_unit_id.id),('product_id', '=', self.product_id.id),
                 ('state', 'in', ['done', 'purchase'])]).sorted(
                key=lambda l: l.order_id.date_order, reverse=True)
            self.last_purchase_date = lines[:1].order_id.date_order
            self.last_price_unit = lines[:1].price_unit
            self.last_supplier_id = lines[:1].order_id.partner_id.id
            self.last_qty = lines[:1].product_qty
            self.last_product_uom_id = lines[:1].product_uom.id

            self._get_product_quantity()