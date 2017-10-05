from openerp import api, fields, models
from lxml import etree
from openerp.tools.translate import _


class InventoryDistributionToShop(models.Model):
    _name = 'stock.distribution.to.shop'
    _rec_name = 'product_tmp_id'
    _order = 'id desc'

    @api.model
    def _Filter_DefaultWareHouse(self):
        return [('id', '=', self.env.ref('stock.warehouse0').id)]

    def _Default_WareHouse_Id(self):
        res = self.env['stock.warehouse'].search([('id', '=', self.env.ref('stock.warehouse0').id)])
        return res and res[0] or False

    # models fields
    received_qty = fields.Float(string='Received Qty')
    distribute_qty = fields.Float(string='Distribute Qty', readonly=True)
    remain_qty = fields.Float(string='Remain Qty', compute='_get_remain_quntity', store=True)
    name = fields.Char('Distribution Reference', readonly=True)
    receive_date = fields.Date(string='Received Date', default=fields.Date.today, required=True, readonly=True)
    notification_date = fields.Date(string='Notification Date', default=fields.Date.today, required=True, readonly=True)

    """ Relational Fields """
    product_tmp_id = fields.Many2one('product.template', string='Product Name', required=True,
                                     domain="[('type', '!=','service')]")
    stock_distribution_lines_ids = fields.One2many('stock.distribution.to.shop.line', 'stock_distributions_id',
                                                   states={'confirm': [('readonly', True)]})
    warehoue_id = fields.Many2one('stock.warehouse', string='Warehouse', default=_Default_WareHouse_Id, required=True)

    state = fields.Selection([
        ('draft', 'Waiting'),
        ('generate', 'Generated'),
        ('confirm', 'Confirm'),
        ('transfer', 'Transfer'),
    ], string='Status', index=True, readonly=True, default='draft', copy=False, states={'draft': [('readonly', False)]})

    @api.one
    def action_generate_distribution_matrix(self):
        if self.warehoue_id and len(self.stock_distribution_lines_ids) == 0:
            vals = []
            stock_quant_obj = self.pool['stock.quant'].read_group(self.env.cr, self.env.uid,
                                                                  domain=[('location_id', '=',
                                                                           self.warehoue_id.lot_stock_id.id), (
                                                                              'product_id.product_tmpl_id.id', '=',
                                                                              self.product_tmp_id.id)],
                                                                  fields=[('product_id'), ('qty')],
                                                                  groupby=[('product_id')]
                                                                  )

            for product in stock_quant_obj:
                product_id = product['product_id'][0]
                on_hand_qty = product['qty']
                pos_config_obj = self.env['pos.config'].search([('active_shop', '=', True)])
                for pos_shop in pos_config_obj:
                    if self.warehoue_id.lot_stock_id.id != pos_shop.stock_location_id.id:
                        distribute_line = {}
                        distribute_line['stock_distributions_id'] = self.id
                        distribute_line['product_id'] = product_id
                        distribute_line['on_hand_qty'] = on_hand_qty
                        distribute_line['source_location_id'] = self.warehoue_id.lot_stock_id.id
                        distribute_line['target_location_id'] = pos_shop.stock_location_id.id
                        distribute_line['pos_shop_id'] = pos_shop.id
                        distribute_line['distribute_qty'] = 0
                        vals.append(distribute_line)

            if vals:
                for distribute_line in vals:
                    self.stock_distribution_lines_ids.create(distribute_line)
                self.state = 'generate'

    @api.multi
    @api.depends('received_qty', 'distribute_qty')
    def _get_remain_quntity(self):
        self.remain_qty = self.received_qty - self.distribute_qty

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('stock_distribution')
        res = super(InventoryDistributionToShop, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        return super(InventoryDistributionToShop, self).write(vals)

    @api.one
    def action_confirm(self):
        self.state = 'confirm'
        for record in self.stock_distribution_lines_ids:
            record.write({'state': 'confirm'})

    @api.one
    def action_transfer(self):
        # self.state = 'transfer'
        return True

        # move_new_obj = self.env['stock.move']
        #
        # stock_picking_hrd = {}
        # stock_picking_hrd['origin'] = self.name
        # stock_picking_hrd['picking_type_id'] = 1
        # picking = self.env['stock.picking'].create(stock_picking_hrd)
        # picking.action_done()
        # for distribute_line in self.stock_distribution_lines_ids:
        #     if distribute_line.distribute_qty > 0:
        #         record = {}
        #         record['picking_id'] = picking.id
        #         record['product_id'] = distribute_line.product_id.id
        #         record['product_uom'] = distribute_line.product_id.uom_id.id
        #         record['name'] = distribute_line.product_id.name
        #         record['product_uom_qty'] = distribute_line.distribute_qty
        #         record['location_id'] = distribute_line.source_location_id.id
        #         record['location_dest_id'] = distribute_line.target_location_id.id
        #         record['procure_method'] = "make_to_stock"
        #         record['state'] = 'draft'
        #         move_insert = move_new_obj.create(record)
        #         print "move id --- ", move_insert.id
        #         move_insert.action_done()
