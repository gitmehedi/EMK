from openerp import api, fields, models
from lxml import etree
from openerp.tools.translate import _


class WarehouseToShopDistribution(models.Model):
    _name = 'warehouse.to.shop.distribution'
    _rec_name = 'shop_id'
    _order = 'id desc'

    """ default data functionality"""

    @api.model
    def _Filter_DefaultWareHouse(self):
        return [('id', '=', self.env.ref('stock.warehouse0').id)]

    def _Default_WareHouse_Id(self):
        res = self.env['stock.warehouse'].search([('id', '=', self.env.ref('stock.warehouse0').id)])
        return res and res[0] or False

    name = fields.Char('Distribution', readonly=True)
    distribute_date = fields.Date(string='Distribute Date', default=fields.Date.today, required=True,
                                  states={'draft': [('readonly', False)]})
    receive_date = fields.Date(string='Received Date',
                               states={'draft': [('readonly', False)], 'transfer': [('readonly', False)]})
    notification_date = fields.Date(string='Notification Date', default=fields.Date.today, required=True, readonly=True)

    """ Relational Fields """
    stock_distribution_lines_ids = fields.One2many('warehouse.to.shop.distribution.line', 'warehouse_distribution_id',
                                                   states={'confirm': [('readonly', True)]},
                                                   string='Product Distribution')
    warehoue_id = fields.Many2one('operating.unit', string='Warehouse', required=True,
                                  states={'draft': [('readonly', False)]})
    shop_id = fields.Many2one('operating.unit', string='Shop Name', required=True,
                              states={'draft': [('readonly', False)]})

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting'),
        ('transfer', 'Transfer'),
        ('received', 'Received'),
        ('done', 'Done'),
    ], string='Status', index=True, readonly=True, default='draft', copy=False,
        states={'draft': [('readonly', False)]})

    @api.one
    def generate_confirm_product(self):
        line_obj = self.env['stock.distribution.to.shop.line']
        shop = self.env['pos.config'].search([('operating_unit_id', '=', self.shop_id.id), ('active_shop', '=', True)])

        distributions = line_obj.search(
            [('target_location_id', '=', shop.stock_location_id.id), ('state', '=', 'draft')])

        for record in distributions:
            if record.distribute_qty > 0:
                rec = {}
                rec['transfer_qty'] = record.distribute_qty
                rec['product_id'] = record.product_id.id
                rec['product_uom_id'] = record.product_id.uom_id.id
                rec['stock_distribution_line_id'] = record.id
                rec['warehouse_distribution_id'] = self.id
                self.stock_distribution_lines_ids.create(rec)
                line_obj.search([('id', '=', record.id)]).write({'state': 'prepare'})

        self.state = 'waiting'

    @api.multi
    @api.depends('received_qty', 'distribute_qty')
    def _get_remain_quntity(self):
        self.remain_qty = self.received_qty - self.distribute_qty

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('warehouse_to_shop_distribution')
        res = super(WarehouseToShopDistribution, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        return super(WarehouseToShopDistribution, self).write(vals)

    @api.one
    def action_transfer(self):
        line_obj = self.env['stock.distribution.to.shop.line']
        move_new_obj = self.env['stock.move']
        warehouse = self.env['pos.config'].search(
            [('operating_unit_id', '=', self.warehoue_id.id), ('active_shop', '=', True)])
        transit_location = self.env['stock.location'].search([('name', 'ilike', 'Inter Company Transit')])

        stock_picking_hrd = {}
        stock_picking_hrd['origin'] = self.name
        stock_picking_hrd['picking_type_id'] = 1
        picking = self.env['stock.picking'].create(stock_picking_hrd)
        picking.action_done()
        for record in self.stock_distribution_lines_ids:
            if record.transfer_qty > 0:
                rec = {}
                rec['picking_id'] = picking.id
                rec['product_id'] = record.product_id.id
                rec['product_uom'] = record.product_id.uom_id.id
                rec['name'] = record.product_id.name
                rec['product_uom_qty'] = record.transfer_qty
                rec['location_id'] = warehouse.stock_location_id.id
                rec['location_dest_id'] = transit_location.id
                rec['procure_method'] = "make_to_stock"
                rec['state'] = 'draft'
                move_insert = move_new_obj.create(rec)
                move_insert.action_done()
                line_obj.search([('id', '=', record.stock_distribution_line_id.id)]).write({'state': 'transfer'})

                record.write({'receive_qty': record.transfer_qty})

        self.state = 'transfer'

    @api.one
    def action_receive(self):
        move_new_obj = self.env['stock.move']
        shop = self.env['pos.config'].search(
            [('operating_unit_id', '=', self.shop_id.id), ('active_shop', '=', True)])
        transit_location = self.env['stock.location'].search([('name', 'ilike', 'Inter Company Transit')])

        stock_picking_hrd = {}
        stock_picking_hrd['origin'] = self.name
        stock_picking_hrd['picking_type_id'] = 1
        picking = self.env['stock.picking'].create(stock_picking_hrd)
        picking.action_done()
        for record in self.stock_distribution_lines_ids:
            if record.transfer_qty > 0:
                rec = {}
                rec['picking_id'] = picking.id
                rec['product_id'] = record.product_id.id
                rec['product_uom'] = record.product_id.uom_id.id
                rec['name'] = record.product_id.name
                rec['product_uom_qty'] = record.transfer_qty
                rec['location_id'] = transit_location.id
                rec['location_dest_id'] = shop.stock_location_id.id
                rec['procure_method'] = "make_to_stock"
                rec['state'] = 'draft'
                move_insert = move_new_obj.create(rec)
                move_insert.action_done()

        self.state = 'received'

    @api.one
    def action_done(self):
        self.state = 'done'
