from datetime import date, datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp import api, fields, models
from openerp.exceptions import Warning


class GoodsReceiveMatrix(models.Model):
    _name = 'goods.receive.matrix'
    _order = 'id desc'

    @api.model
    def _company_default_get(self):
        if self.env.user.company_id:
            return self.env.user.company_id

    """ Required and Optional Fields """
    readonly_check = fields.Boolean(default=False)
    receive_visible = fields.Boolean(default=False)
    quantity = fields.Float(size=17, digits=(15, 2), string='Order Quantity', readonly=True)
    receive_qty = fields.Float(size=17, digits=(15, 2), string='Received Quantity', readonly=True)
    price_unit = fields.Float(size=17, digits=(15, 2), string='Unit Price')
    receive_date = fields.Datetime(default=fields.Datetime.now, string='Recieved Date')

    """ Relational Fields """
    po_no = fields.Many2one('purchase.order', string="Order Number", required=True,
                            domain=[('state', '=', 'approved')])
    product_tmpl_id = fields.Many2one('product.template', related='line_id.product_id', store=True, readonly=True)
    product_image = fields.Binary(related='line_id.product_id.image', store=True, readonly=True)
    line_id = fields.Many2one('purchase.order.line', string="Line", required=True)

    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse", required=True)
    uom = fields.Many2one('product.uom', string="UOM", ondelete='set null', readonly=True)

    matrix_line_ids = fields.One2many('goods.receive.matrix.line', 'matrix_id',
                                      string="Matrix Line")
    company_id = fields.Many2one('res.company', string='Company',default=_company_default_get)

    state = fields.Selection([('draft', 'Draft'), ('waiting', 'Waiting For Approval'), ('adjustment', 'Adjustment'),
                              ('approved', 'Approved'), ('received', 'Received'), ('cancelled', 'Cancelled')],
                             default="draft", readonly=True)

    _rec_name = "po_no"

    """ Functions and it's Operation """

    @api.model
    def create(self, vals):
        purchase_order_line = self.env['purchase.order.line'].search([('id', '=', vals['line_id'])])
        vals['uom'] = purchase_order_line.product_uom.id
        vals['quantity'] = purchase_order_line.product_qty
        vals['receive_qty'] = purchase_order_line.receive_qty
        vals['price_unit'] = purchase_order_line.price_unit
        return super(GoodsReceiveMatrix, self).create(vals)

    @api.multi
    def write(self, vals):
        # TODO: process before updating resource
        purchase_order_line = self.line_id
        vals['quantity'] = purchase_order_line.product_qty
        vals['receive_qty'] = purchase_order_line.receive_qty
        vals['price_unit'] = purchase_order_line.price_unit
        vals['receive_date'] = fields.Datetime.now()
        res = super(GoodsReceiveMatrix, self).write(vals)
        self.action_submit(vals)

        return res

    @api.multi
    def action_submit(self, vals):
        for p_id in self:
            master_id = p_id.matrix_line_ids

        po_pool = self.env['purchase.order']
        picking_pool = self.env['stock.picking']
        mov_obj = self.env['stock.move']

        location_id = self.warehouse_id.pick_type_id.default_location_src_id.id
        location_dest_id = self.warehouse_id.pick_type_id.default_location_dest_id.id

        po_no_info = po_pool.search([('id', '=', self.po_no.id)])

        if not po_no_info:
            raise Warning(_('Product is not available with this purchase order.'))
        return True

    @api.multi
    def prepare_receive_matrix(self):
        generate_matrix = self.env['goods.receive.matrix'].browse([self.id])
        generate_matrix.readonly_check = True
        generate_matrix.receive_visible = True

        matrix_line_obj = self.env['goods.receive.matrix.line']
        for matrix in generate_matrix:
            """
            If there are inventory lines already (e.g. from import),
            respect those and set their theoretical qty
            """

            matrix_line_ids = [line.id for line in matrix.matrix_line_ids]
            if not matrix_line_ids:
                """ compute the matrix lines and create them """
                vals = self._get_receive_matrix_lines(matrix)
                for product_line in vals:
                    # if product_line['product_id']:
                    matrix_line_obj.create(product_line)
        return self.write({})

    @api.multi
    def _get_receive_matrix_lines(self, matrix):
        vals, color, size = [], [], []
        for col_siz in matrix.product_tmpl_id.attribute_line_ids:
            if col_siz.attribute_id.name == 'Size':
                color = col_siz.value_ids.ids
            else:
                size = col_siz.value_ids.ids

        for record in matrix.product_tmpl_id.product_variant_ids:

            if len(record.attribute_line_ids) == 2:
                rec = {}

                if record.attribute_value_ids[0].id in color:
                    rec['matrix_id'] = matrix.id
                    rec['product_id'] = record.id
                    rec['product_uom_id'] = record.uom_id.id
                    rec['size_variant_id'] = record.attribute_value_ids[1].id
                    rec['color_variant_id'] = record.attribute_value_ids[0].id
                    vals.append(rec)
                else:
                    rec['matrix_id'] = matrix.id
                    rec['product_id'] = record.id
                    rec['product_uom_id'] = record.uom_id.id
                    rec['size_variant_id'] = record.attribute_value_ids[0].id
                    rec['color_variant_id'] = record.attribute_value_ids[1].id
                    vals.append(rec)
            else:
                raise Warning(_('Please Create Product According To Pebbles Product Creating Instruction'))

        return vals

    @api.multi
    def action_receive(self, vals):

        for p_id in self:
            master_id = p_id.matrix_line_ids

        po_pool = self.env['purchase.order']
        po_line_pool = self.env['purchase.order.line']
        po_line_pool_info = po_line_pool.search([('id', '=', self.line_id.id)])
        picking_pool = self.env['stock.picking']
        mov_obj = self.env['stock.move']
        move_new_obj = self.pool['stock.move']

        location_id = self.warehouse_id.in_type_id.default_location_src_id.id
        location_dest_id = self.warehouse_id.in_type_id.default_location_dest_id.id

        po_no_info = po_pool.search([('id', '=', self.po_no.id)])
        purchased_qty = self.line_id.product_qty
        self.env.cr.execute(''' SELECT sum(ml.product_qty) as product_qty
                FROM goods_receive_matrix  m, goods_receive_matrix_line ml WHERE m.id= ml.matrix_id
                AND m.state != 'cancelled' AND m.po_no = %s AND m.line_id = %s 
                GROUP BY m.line_id ''' % (self.po_no.id, self.line_id.id))

        receive_qty = 0;
        if self.env.cr.rowcount == 0:
            print self.env.cr.rowcount
        else:
            for line_qty in self.env.cr.dictfetchall():
                print "line_qty", line_qty
                receive_qty = line_qty['product_qty']
        if not po_no_info:
            raise Warning(_('Product is not available with this purchase order.'))
        # for po_record in po_no_info:

        if (receive_qty > purchased_qty and self.state != "approved"):
            self.state = "waiting"
            return True
        else:
            self.env.cr.execute(''' SELECT sum(ml.product_qty) as product_qty
                FROM goods_receive_matrix  m, goods_receive_matrix_line ml WHERE m.id= ml.matrix_id
                AND m.state = 'received' AND m.po_no = %s AND m.line_id = %s 
                GROUP BY m.line_id ''' % (self.po_no.id, self.line_id.id))
            for total_receive_qty in self.env.cr.dictfetchall():
                if (total_receive_qty['product_qty'] > purchased_qty):
                    raise Warning(_('Purchased quantity is not available.'))

            mov_quant = self.env['stock.quant']
            for po_record in self:
                pick_vals = {
                    'picking_type_id': self.warehouse_id.in_type_id.id,
                    'state': 'done',
                    'partner_id': po_no_info.partner_id.id,
                    'date': fields.Datetime.now(),
                }
                picking_id = picking_pool.create(pick_vals)

                for line in po_record.matrix_line_ids:
                    if (line.product_qty > 0):
                        vals = {
                            'product_id': line.product_id.id,
                            'product_uos_qty': line.product_qty,
                            'product_uom_qty': line.product_qty,
                            'name': line.product_id.name,
                            'picking_type_id': self.warehouse_id.in_type_id.id,
                            'product_uom': line.product_id.uom_id.id,
                            'location_id': location_id,
                            'location_dest_id': location_dest_id,
                            'date_expected': date.today(),
                            'picking_id': picking_id.id,
                            'price_unit': self.price_unit,
                            'state': 'done',
                        }
                        print "Json obj ", vals
                        move_id = mov_obj.create(vals)

                        # Stock quant start

                        location = location_dest_id

                        vals = {
                            'product_id': line.product_id.id,
                            'location_id': location,
                            'qty': line.product_qty,
                            'cost': self.price_unit,
                            'in_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                            'company_id': self.warehouse_id.company_id.id,
                        }

                        move_new_obj.action_done(self.env.cr, self.env.uid, [move_id.id])

            self.state = "received"

            """ Update receive qty in the purchase line order """

            self.env.cr.execute(''' SELECT sum(ml.product_qty) as product_qty
            FROM goods_receive_matrix  m, goods_receive_matrix_line ml WHERE m.id= ml.matrix_id
            AND m.state = 'received' AND m.po_no = %s AND m.line_id = %s 
            GROUP BY m.line_id ''' % (self.po_no.id, self.line_id.id))

            purchase_order_line = {}
            if self.env.cr.rowcount == 0:
                purchase_order_line = {
                    'receive_qty': 0,
                }
                po_line_pool_info.write(purchase_order_line)
            else:
                for line_qty in self.env.cr.dictfetchall():
                    receive_qty = line_qty['product_qty']
                    purchase_order_line = {
                        'receive_qty': receive_qty,
                    }
                    po_line_pool_info.write(purchase_order_line)

            self.receive_qty = purchase_order_line['receive_qty']

            """ Update purchase_order state info when all line received """
            po_line_obj_by_po = po_line_pool.search([('order_id', '=', self.po_no.id)])
            po_state = False
            for po_line_obj_by_po_info in po_line_obj_by_po:
                if (po_line_obj_by_po_info.product_qty > po_line_obj_by_po_info.receive_qty):
                    po_state = True

            if (self.line_id.receive_qty >= self.line_id.product_qty):
                po_line_state_val = {
                    'state': 'done'
                }
                po_line_pool_info.write(po_line_state_val)

            if (po_state == False):
                po_state_val = {
                    'state': 'done',
                }
                po_no_info.write(po_state_val)

            stock_distribution = {}
            stock_distribution['product_tmp_id'] = self.line_id.product_id.id
            stock_distribution['received_qty'] = sum(prod.product_qty for prod in self.matrix_line_ids)
            stock_distribution['warehoue_id'] = self.warehouse_id.id
            self.env['stock.distribution.to.shop'].create(stock_distribution)

        return True

    @api.multi
    def action_adjustment(self, vals):
        self.state = "adjustment"
        return True

    @api.multi
    def action_cancel(self, vals):
        self.state = "cancelled"
        return True

    @api.multi
    def action_approved(self, vals):
        self.state = "approved"
        return True

    @api.onchange('line_id')
    def _product_uom(self):
        print "self", self.line_id.product_uom.id
        self.uom = self.line_id.product_uom.id
        self.quantity = self.line_id.product_qty
        self.receive_qty = self.line_id.receive_qty

    @api.onchange('po_no')
    def _delivery_warehouse(self):
        self.warehouse_id = self.po_no.picking_type_id.warehouse_id.id
        self.line_id = False

    def _compute_product_template(self):
        product_ids = []
        result = {}
        val = {}
        if self.po_no:
            for line in self.po_no.order_line:
                product_ids.append(line.product_id.id)

            domain = [
                ('id', 'in', product_ids)
            ]
            result = {
                'domain': {
                    'product_id': domain,
                },
            }

        return result

    @api.multi
    def unlink(self):
        for p_id in self:
            if (p_id.state == "received"):
                raise Warning(_("You have already received this order. So, can't delete this record."))
            else:
                matrix_line = self.env['goods.receive.matrix'].search([('id', '=', p_id.id)])
                super(GoodsReceiveMatrix, matrix_line).unlink()
        return True
