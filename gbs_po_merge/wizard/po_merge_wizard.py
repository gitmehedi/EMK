from datetime import datetime, date
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class POMergeWizard(models.TransientModel):
    _name = 'po.merge.wizard'

    def _get_default_po_ids(self):
        if self.env.context.get('default_is_new_add'):
            return False
        else:
            for po_obj in self.env['purchase.order'].search([('id', 'in', self.env.context.get('active_ids'))]):
                if po_obj.state in ['purchase','done','cancel']:
                    raise UserError(_('Already Ordered or cancelled Quotation can not be merge.'))
                else:
                    pass
            return self.env.context.get('active_ids')

    def _get_default_operating_unit(self):
        if self.env.context.get('operating_unit_id'):
            return self.env.context.get('operating_unit_id')
        else:
            op_ids = [i.operating_unit_id.id for i in self.env['purchase.order'].search([('id','in',self.env.context.get('active_ids'))])]
            if (len(set(op_ids)) == 1):
                return op_ids[0]
            else:
                raise UserError(_('Operating unit must be same.'))

    def _get_default_partner(self):
        if self.env.context.get('partner_id'):
            return self.env.context.get('partner_id')
        else:
            partner_ids = [i.partner_id.id for i in
                      self.env['purchase.order'].search([('id', 'in', self.env.context.get('active_ids'))])]
            if (len(set(partner_ids)) == 1):
                return partner_ids[0]
            else:
                raise UserError(_('Supplier must be same.'))


    po_ids = fields.Many2many('purchase.order', string='Select Quotation',
                              default=_get_default_po_ids)
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        default=_get_default_operating_unit)
    partner_id = fields.Many2one('res.partner',string='Partner',
                                 default=_get_default_partner)
    product_lines = fields.One2many('po.merge.line.wizard', 'merge_id', string='Product(s)')
    is_new_add = fields.Boolean('Is New Add',default=False,help="It define that,this wizard for marge or add.")

    @api.multi
    @api.onchange('operating_unit_id','partner_id')
    def _onchange_op_partner(self):
        for wiz in self:
            if wiz.operating_unit_id and wiz.partner_id:
                return {'domain': {'po_ids': [('operating_unit_id', '=', wiz.operating_unit_id.id),('partner_id','=',wiz.partner_id.id),
                                              ('state','in',('draft','sent','to approve'))]}}
            else:
                wiz.po_ids = []


    @api.onchange('po_ids')
    def _onchange_po_ids(self):
        if self.po_ids:
            vals = []
            for po_id in self.po_ids:
                if not self.operating_unit_id:
                    self.operating_unit_id = po_id.operating_unit_id.id
                if not self.partner_id:
                    self.partner_id = po_id.partner_id.id
                line_pool = self.env['purchase.order.line'].search([('order_id', '=', po_id.id)])
                for obj in line_pool:
                    vals.append((0, 0, {'product_id': obj.product_id,
                                        'product_qty': obj.product_qty,
                                        'product_uom_id': obj.product_uom.id,
                                        'price_unit': obj.price_unit,
                                        }))
                self.product_lines = vals
        elif self.is_new_add:
            self.product_lines = []
        else:
            self.operating_unit_id = False
            self.partner_id = False
            self.product_lines = []



    def action_confirm(self):
        po_obj = self.env['purchase.order']
        po_line_obj = self.env['purchase.order.line']
        date_order = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        if not self.is_new_add:
            order_id= False

            if not self.product_lines:
                raise UserError(_('Unable to merge without product. Please add product(s).'))

            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', 'incoming'),
                 ('warehouse_id.operating_unit_id', '=', self.operating_unit_id.id)], order='id ASC', limit=1)
            if not picking_type:
                raise UserError(_('Please create picking type or contact with your system administrator.'))

            po_name = self.env['ir.sequence'].next_by_code_new('purchase.quotation', date.today(),self.operating_unit_id) or '/'

            res_order = {
                'name': po_name,
                'picking_type_id': picking_type.id,
                'operating_unit_id': self.operating_unit_id.id,
                'partner_id': self.partner_id.id,
                'currency_id': self.partner_id.property_purchase_currency_id.id,
                'company_id': self.env.user.company_id.id,
                'date_order': date_order,
                'date_planned': date_order,
                'state': 'draft',
            }

            order = po_obj.create(res_order)
            if order:
                order_id = order.id

            # for line in self.product_lines:
            product_list = []
            for obj in self.product_lines:
                if obj.product_id not in product_list:
                    product_list.append(obj.product_id)

            list_new = self.product_lines
            new_list = []
            for obj in product_list:
                count = 0
                qty = 0
                for ele in list_new:
                    if obj == ele.product_id:
                        count += 1
                        qty += ele.product_qty
                        if count == 1:
                            new_list.append(ele)
                for att in new_list:
                    if obj == att.product_id:
                        att.product_qty = qty

            for line in new_list:
                res_order_line = {
                    'product_id' : line.product_id.id,
                    'product_uom' : line.product_uom_id.id,
                    'name' : line.product_id.display_name,
                    'date_planned': date_order,
                    'order_id': order_id,
                    'price_unit': line.price_unit,
                    'product_qty': line.product_qty,
                }
                po_line_obj.create(res_order_line)

            view_id = self.env.ref('purchase.purchase_order_form')

            return {
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id and view_id.id or False,
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order',
                'res_id': order_id,
                'target': 'current',
            }
        else:
            # for line in self.product_lines:
            product_list = []
            for obj in self.product_lines:
                if obj.product_id not in product_list:
                    product_list.append(obj.product_id)

            list_new = self.product_lines
            new_list = []
            for obj in product_list:
                count = 0
                qty = 0
                for ele in list_new:
                    if obj == ele.product_id:
                        count += 1
                        qty += ele.product_qty
                        if count == 1:
                            new_list.append(ele)
                for att in new_list:
                    if obj == att.product_id:
                        att.product_qty = qty

            for line in new_list:
                if line.product_id.id in [i.product_id.id for i in po_line_obj.search([('order_id', '=', self.env.context.get('active_id'))])]:
                    obj = po_line_obj.search([('order_id', '=', self.env.context.get('active_id')),('product_id','=',line.product_id.id)])[0]
                    obj.write({'product_qty': obj.product_qty + line.product_qty})
                else:
                    res_order_line = {
                        'product_id': line.product_id.id,
                        'product_uom': line.product_uom_id.id,
                        'name': line.product_id.display_name,
                        'date_planned': date_order,
                        'order_id': self.env.context.get('active_id'),
                        'price_unit': line.price_unit,
                        'product_qty': line.product_qty,
                    }
                    po_line_obj.create(res_order_line)

            return {'type': 'ir.actions.act_window_close'}



class POMergeLineWizard(models.TransientModel):
    _name = 'po.merge.line.wizard'

    merge_id = fields.Many2one('po.merge.wizard', string='Merge Id', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True, ondelete='cascade')
    product_qty = fields.Float(string='Quantity')
    price_unit = fields.Float(related='product_id.standard_price',string='Price Unit')
    product_uom_id = fields.Many2one(related='product_id.uom_id',comodel='product.uom', string='Unit of Measure')
