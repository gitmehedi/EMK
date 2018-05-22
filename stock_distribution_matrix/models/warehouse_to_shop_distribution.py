from datetime import datetime
from lxml import etree

from openerp import api, fields, models
from openerp.tools.translate import _
from openerp.exceptions import ValidationError, Warning


class WarehouseToShopDistribution(models.Model):
    _name = 'warehouse.to.shop.distribution'
    _rec_name = 'name'
    _order = 'id desc'

    """ default data functionality"""

    @api.model
    def default_warehouse(self):
        return self.env['stock.warehouse'].search([], order='id asc', limit=1)

    @api.model
    def _company_default_get(self):
        if self.env.user.company_id:
            return self.env.user.company_id

    name = fields.Char('Distribution', readonly=True)
    distribute_date = fields.Date(string='Distribute Date', default=fields.Date.today, required=True, readonly=True,
                                  states={'draft': [('readonly', False)]})
    receive_date = fields.Date(string='Received Date', readonly=True,
                               states={'draft': [('readonly', False)], 'transfer': [('readonly', False)]})
    notification_date = fields.Date(string='Notification Date', default=fields.Date.today, required=True, readonly=True)

    """ Relational Fields """
    stock_distribution_lines_ids = fields.One2many('warehouse.to.shop.distribution.line', 'warehouse_distribution_id',
                                                   states={'confirm': [('readonly', True)]},
                                                   string='Product Distribution')
    warehoue_id = fields.Many2one('operating.unit', string='Warehouse')

    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True, readonly=True,
                                   default=default_warehouse,
                                   states={'draft': [('readonly', False)]})

    shop_id = fields.Many2one('operating.unit', string='Shop Name', required=True, readonly=True,
                              states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string='Company', default=_company_default_get)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting'),
        ('transfer', 'Transfer'),
        ('received', 'Received'),
    ], string='Status', index=True, readonly=True, default='draft', copy=False,
        states={'draft': [('readonly', False)]})

    @api.one
    def generate_confirm_product(self):
        line_obj = self.env['stock.distribution.to.shop.line']
        shop = self.env['pos.config'].search([('operating_unit_id', '=', self.shop_id.id), ('active_shop', '=', True)])

        distributions = line_obj.search(
            [('target_location_id', '=', shop.stock_location_id.id), ('state', '=', 'confirm'),
             ('distribute_qty', '>', 0)])
        if not distributions:
            raise Warning(_("No product available to distribution. Please create stock distribution."))

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

    @api.multi
    def unlink(self):
        for record in self:
            if record.state == 'draft':
                super(WarehouseToShopDistribution, record).unlink()
            else:
                raise Warning(_("You cann't delete a distribution except draft state."))

    def get_picking(self, src_loc, dest_loc):
        picking_type = self.env['stock.picking.type'].search([('default_location_src_id', '=', src_loc.id),
                                                              ('default_location_dest_id', '=', dest_loc.id)],
                                                             order='id asc', limit=1)
        if not picking_type:
            raise ValidationError(_('Please Create a Picking Type, Otherwise your operation will not continue.'))

        picking_val = {
            'picking_type_id': picking_type.id,
            'priority': '1',
            'move_type': 'direct',
            'company_id': self.env.user['company_id'].id,
            'warehouse_transfer_id': self.id,
            'dest_operating_unit_id': self.shop_id.id,
            'state': 'done',
            'invoice_state': 'none',
        }
        picking = self.env['stock.picking'].create(picking_val)
        picking.action_done()

        return picking

    @api.one
    def action_transfer(self):
        if self.state != 'waiting':
            raise ValidationError(_('Please Create a Picking Type, Otherwise your operation will not continue.'))

        line_obj = self.env['stock.distribution.to.shop.line']
        move_new_obj = self.env['stock.move']

        warehouse_loc = self.env['stock.location'].search(
            [('operating_unit_id', '=', self.warehouse_id.operating_unit_id.id)], limit=1)
        transit_loc = self.env['stock.location'].search([('name', 'ilike', 'Inter Company Transit')])

        picking = self.get_picking(src_loc=warehouse_loc, dest_loc=transit_loc)

        for record in self.stock_distribution_lines_ids:
            if record.transfer_qty > 0:
                rec = {}
                rec['picking_id'] = picking.id
                rec['product_id'] = record.product_id.id
                rec['product_uom'] = record.product_id.uom_id.id
                rec['name'] = record.product_id.name
                rec['product_uom_qty'] = record.transfer_qty
                rec['location_id'] = warehouse_loc.id
                rec['location_dest_id'] = transit_loc.id
                rec['procure_method'] = "make_to_stock"
                rec['state'] = 'draft'
                move_insert = move_new_obj.create(rec)
                move_insert.action_done()
                line_obj.search([('id', '=', record.stock_distribution_line_id.id)]).write({'state': 'transfer'})

                record.write({'receive_qty': record.transfer_qty, 'is_transfer': True})

        self.state = 'transfer'

    @api.one
    def action_receive(self):
        if self.state != 'transfer':
            raise ValidationError(_('Please Create a Picking Type, Otherwise your operation will not continue.'))

        move_new_obj = self.env['stock.move']

        transit_location = self.env['stock.location'].search([('name', 'ilike', 'Inter Company Transit')])
        dest_loc = self.env['stock.location'].search([('operating_unit_id', '=', self.shop_id.id)])

        picking = self.get_picking(src_loc=transit_location, dest_loc=dest_loc)

        for record in self.stock_distribution_lines_ids:
            if record.transfer_qty > 0:
                rec = {}
                rec['picking_id'] = picking.id
                rec['product_id'] = record.product_id.id
                rec['product_uom'] = record.product_id.uom_id.id
                rec['name'] = record.product_id.name
                rec['product_uom_qty'] = record.transfer_qty
                rec['location_id'] = transit_location.id
                rec['location_dest_id'] = dest_loc.id
                rec['procure_method'] = "make_to_stock"
                rec['state'] = 'draft'
                move_insert = move_new_obj.create(rec)
                move_insert.action_done()
                record.write({'is_receive': True})

        self.receive_date = self.get_current_date()
        self.state = 'received'

    @api.one
    def action_done(self):
        self.state = 'done'

    @api.model
    def get_current_date(self):
        return datetime.today()


class InheriteStockPicking(models.Model):
    _inherit = 'stock.picking'

    warehouse_transfer_id = fields.Many2one('warehouse.to.shop.distribution', string='Warehouse Transfer')
