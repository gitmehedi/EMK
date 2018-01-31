import datetime

from openerp import api, models, fields, exceptions
from openerp.tools.translate import _
from openerp.exceptions import ValidationError


class StockTransferRequest(models.Model):
    """
    Send product to other shop
    """
    _name = 'stock.transfer.request'
    _rec_name = "name"
    _order = "id desc"

    @api.model
    def _default_operating_unit(self):
        return self.env.user.default_operating_unit_id

    barcode = fields.Char(string='Product Barcode', size=20,
                          readonly=True, states={'draft': [('readonly', False)]})

    name = fields.Char('Challan No', readonly=True)
    submit_date = fields.Datetime(string="Submit Date", readonly=True,
                                  states={'draft': [('readonly', False)], 'transfer': [('readonly', False)]})
    approve_date = fields.Datetime(string="Approve Date", readonly=True,
                                   states={'submit': [('readonly', False)]})
    transfer_date = fields.Datetime(string="Transfer Date", readonly=True,
                                    states={'approve': [('readonly', False)]})
    receive_date = fields.Datetime(string="Receive Date", readonly=True,
                                   states={'transfer': [('readonly', False)]})

    """ Relational Fields """
    product_line_ids = fields.One2many('stock.transfer.request.line', 'stock_transfer_id', readonly=True,
                                       states={'draft': [('readonly', False)], 'transfer': [('readonly', False)]})
    my_shop_id = fields.Many2one('operating.unit', string="My Shop", required=True, ondelete="cascade",
                                 default=_default_operating_unit, store=True,
                                 readonly=True, states={'draft': [('readonly', False)]})
    transfer_shop_id = fields.Many2one('operating.unit', string="To Shop", store=True, required=True,
                                       ondelete="cascade",
                                       readonly=True, states={'draft': [('readonly', False)]})
    is_transfer = fields.Boolean(string="Is Transfer", default=False)
    is_receive = fields.Boolean(string="Is Receive", default=False)

    """ Approval Process User """
    submit_user_id = fields.Many2one('res.users', string="Submit User")
    approve_user_id = fields.Many2one('res.users', string="Approve User")
    transfer_user_id = fields.Many2one('res.users', string="Transfer User")
    receive_user_id = fields.Many2one('res.users', string="Receive User")

    """ States Fields """
    state = fields.Selection([('draft', "Draft"), ('submit', "Submit"), ('approve', "Approved"),
                              ('transfer', "Transfer"), ('receive', "Received"), ('reject', "Rejected")], default='draft')

    @api.onchange('barcode')
    def _onchange_barcode(self):
        if self.barcode:
            product = self.env['product.product'].search([('default_code', '=', self.barcode)])
            product_line_ids = self.product_line_ids
            if product:
                list = [p.product_id.id for p in product_line_ids]

                if self.state == 'transfer':
                    location_id = self.env['pos.config'].search([('operating_unit_id', '=', self.my_shop_id.id)])

                    quant = self.env['stock.quant'].search([('product_id', '=', product.id),
                                                            ('location_id', '=', self.get_location())])
                else:
                    location_id = self.env['pos.config'].search([('operating_unit_id', '=', self.my_shop_id.id)])

                    quant = self.env['stock.quant'].search([('product_id', '=', product.id),
                                                            ('location_id', '=', self.get_location())])

                sumval = sum([val.qty for val in quant])

                if product.id in list:
                    for k in product_line_ids:
                        quantity = k.quantity + 1 if product.id == k.product_id.id else k.quantity
                        final_qty = quantity if sumval > quantity else sumval
                        k.update({'quantity': final_qty})
                else:
                    if not sumval:
                        return {'warning': {
                            'title': _('Insufficient Balance!'),
                            'message': _('[{0}] has not sufficient quantity'.format(product.name))
                        }
                        }

                    product_line_ids += product_line_ids.new({
                        'product_id': product.id,
                        'quantity': 1,
                        'store_qty': sumval
                    })
                    self.product_line_ids = product_line_ids
            self.barcode = None

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'stock.transfer.request') or '/'
        return super(StockTransferRequest, self).create(vals)

    @api.one
    def action_draft(self):
        self.state = 'draft'

    @api.one
    def action_submit(self):
        self.state = 'submit'
        self.submit_date = self.get_current_date()
        self.submit_user_id = self.get_login_user()

    @api.one
    def action_approve(self):
        self.state = 'approve'
        self.approve_date = self.get_current_date()
        self.approve_user_id = self.get_login_user()

    def get_picking(self, source_loc, dest_loc):
        picking_type = self.env['stock.picking.type'].search([('default_location_src_id', '=', source_loc),
                                                              ('default_location_dest_id', '=', dest_loc)],
                                                             order='id asc', limit=1)
        if not picking_type:
            raise ValidationError(_('Please Create a Picking Type, Otherwise your operation will not continue.'))

        picking_val = {
            'picking_type_id': picking_type.id,
            'priority': '1',
            'move_type': 'direct',
            'company_id': self.env.user['company_id'].id,
            'dest_operating_unit_id': self.transfer_shop_id.id,
            'stock_transfer_id': self.id,
            'state': 'done',
            'invoice_state': 'none',
        }
        picking = self.env['stock.picking'].create(picking_val)
        picking.action_done()

        return picking

    @api.one
    def action_transfer(self):
        if self.state != 'approve':
            raise ValidationError(_('Please transfer product in validate state.'))

        move_obj = self.env['stock.move']
        transit_location = self.env['stock.location'].search([('name', 'ilike', 'Inter Company Transit')])
        shop_location = self.get_location(self.my_shop_id.id)
        picking = self.get_picking(source_loc=shop_location, dest_loc=transit_location.id)

        for val in self.product_line_ids:
            if val:
                move = {}
                move['picking_id'] = picking.id
                move['product_id'] = val.product_id.id
                move['product_uom'] = val.product_id.uom_id.id
                move['product_uos_qty'] = val.quantity
                move['picking_id'] = picking.id
                move['product_uom_qty'] = val.quantity
                move['name'] = val.product_id.name
                move['price_unit'] = val.product_id.price
                move['invoice_state'] = 'invoiced'
                move['date_expected'] = '{0}'.format(datetime.date.today())
                move['location_id'] = shop_location
                move['location_dest_id'] = transit_location.id
                move['procure_method'] = "make_to_stock"
                move_done = move_obj.create(move)
                move_done.action_done()

        self.state = 'transfer'
        self.transfer_date = self.get_current_date()
        self.transfer_user_id = self.get_login_user()
        self.is_transfer = True

    @api.one
    def action_receive(self):
        if self.state != 'transfer':
            raise ValidationError(_('Please transfer product in validate state.'))

        move_obj = self.env['stock.move']
        transit_location = self.env['stock.location'].search([('name', 'ilike', 'Inter Company Transit')])
        shop_location = self.get_location(self.transfer_shop_id.id)
        picking = self.get_picking(source_loc=transit_location.id, dest_loc=shop_location)

        for val in self.product_line_ids:
            if val:
                move = {}
                move['picking_id'] = picking.id
                move['product_id'] = val.product_id.id
                move['product_uom'] = val.product_id.uom_id.id
                move['product_uos_qty'] = val.quantity
                move['picking_id'] = picking.id
                move['product_uom_qty'] = val.quantity
                move['name'] = val.product_id.name
                move['price_unit'] = val.product_id.price
                move['invoice_state'] = 'invoiced'
                move['date_expected'] = '{0}'.format(datetime.date.today())
                move['location_id'] = transit_location.id
                move['location_dest_id'] = shop_location
                move['procure_method'] = "make_to_stock"
                move_done = move_obj.create(move)
                move_done.action_done()

        self.state = 'receive'
        self.receive_date = self.get_current_date()
        self.receive_user_id = self.get_login_user()
        self.is_receive = True

    @api.one
    def action_reject(self):
        self.state = 'reject'
        self.receive_date = self.get_current_date()
        self.receive_user_id = self.get_login_user()

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ['draft', 'submit']:
                raise exceptions.ValidationError(
                    "You cannot delete a record with state approve, transfer or receive state.")
            rec.unlink()
        return super(StockTransferRequest, self).unlink()

    def get_location(self, operating_unit):
        location = self.env['pos.config'].search([('operating_unit_id', '=', operating_unit)])
        if location:
            return location[0].stock_location_id.id

    @api.model
    def get_login_user(self):
        return self.env.user.id

    @api.model
    def get_current_date(self):
        return datetime.datetime.today()

    @api.one
    def action_send_loss_inventory(self):
        if self.state != 'receive':
            raise ValidationError(_('Please transfer product in validate state.'))

        move_obj = self.env['stock.move']
        src_loc = self.get_location(self.transfer_shop_id.id)
        dest_loc = self.env['stock.location'].search([('name', 'ilike', 'Inventory loss')])

        picking = self.get_picking(source_loc=src_loc, dest_loc=dest_loc.id)

        for val in self.product_line_ids:
            if val:
                move = {}
                move['picking_id'] = picking.id
                move['product_id'] = val.product_id.id
                move['product_uom'] = val.product_id.uom_id.id
                move['product_uos_qty'] = val.quantity
                move['picking_id'] = picking.id
                move['product_uom_qty'] = val.quantity
                move['name'] = val.product_id.name
                move['price_unit'] = val.product_id.price
                move['invoice_state'] = 'invoiced'
                move['date_expected'] = '{0}'.format(datetime.date.today())
                move['location_id'] = src_loc
                move['location_dest_id'] = dest_loc.id
                move['procure_method'] = "make_to_stock"
                move_done = move_obj.create(move)
                move_done.action_done()

        self.state = 'reject'
        self.receive_date = self.get_current_date()
        self.receive_user_id = self.get_login_user()


class InheriteStockPicking(models.Model):
    _inherit = 'stock.picking'

    stock_transfer_id = fields.Many2one('stock.transfer.request', string='Stock Transfer')
