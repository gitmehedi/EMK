from openerp import api, fields, models
from lxml import etree
class inventory_distribution_to_shop(models.Model):
    _name = 'stock.distribution.to.shop'
    _rec_name = 'product_tmp_id' 
    
    @api.model
    def _Filter_DefaultWareHouse(self):
        return [('id', '=', self.env.ref('stock.warehouse0').id)]

    
    def _Default_WareHouse_Id(self):
        res = self.env['stock.warehouse'].search([('id', '=', self.env.ref('stock.warehouse0').id)])
        return res and res[0] or False
 
    stock_distribution_lines_ids = fields.One2many('stock.distribution.to.shop.line', 'stock_distributions_id',states={'confirm':[('readonly', True)]})
    
    product_tmp_id = fields.Many2one('product.template',string='Product Template')
    received_qty = fields.Float(string='Received Qty')
    distribute_qty = fields.Float(string='Distribute Qty',readonly=True)
    remain_qty = fields.Float(string='Remain Qty',compute='_get_remain_quntity',store=True)
    
#     warehoue_id = fields.Many2one('stock.warehouse',string='Warehouse',domain=_Filter_DefaultWareHouse,default=_Default_WareHouse_Id)
    warehoue_id = fields.Many2one('stock.warehouse',string='Warehouse',default=_Default_WareHouse_Id)
    
    name=fields.Char('Distribution Ref#',readonly=True)
    receive_date = fields.Date(string='Received Date', default=fields.Date.today, required=True, readonly=True)
    notification_date = fields.Date(string='Notification Date', default=fields.Date.today, required=True, readonly=True)
    
    
    state = fields.Selection([
               ('draft','Waiting'),
               ('generate','Generated'),
               ('confirm','Confirm'),
               ('transfer','Transfer'),
           ], string='Status', index=True, readonly=True, default='draft',copy=False,states={'draft':[('readonly', False)]})
    


    @api.one
    def action_generate_distribution_matrix(self):
        self.state = 'generate'   
        """
        Generate Matrix Use Case
        -------------------------------------------- 
            1. if User select Warehouse
            2. Before not Generate (matrix generate once a time) 
        """
        if self.warehoue_id and len(self.stock_distribution_lines_ids)==0:
            vals = []
            stock_quant_obj=self.pool['stock.quant'].read_group(self.env.cr,self.env.uid,
                                       domain=[('location_id','=',self.warehoue_id.lot_stock_id.id),('product_id.product_tmpl_id.id','=',self.product_tmp_id.id)],
                                       fields=[('product_id'),('qty')],
                                       groupby=[('product_id')]
                                       )
             
            for product in stock_quant_obj:
                product_id=product['product_id'][0]
                on_hand_qty=product['qty']
                pos_config_obj=self.env['pos.config'].search([])
                for pos_shop in pos_config_obj:
                    if self.warehoue_id.lot_stock_id.id!=pos_shop.stock_location_id.id:
                        distribute_line={}
                        distribute_line['stock_distributions_id']=self.id
                        distribute_line['product_id'] =product_id
                        distribute_line['on_hand_qty'] =on_hand_qty
                        distribute_line['source_location_id'] =self.warehoue_id.lot_stock_id.id
                        distribute_line['target_location_id'] =pos_shop.stock_location_id.id
                        distribute_line['pos_shop_id'] =pos_shop.id
                        distribute_line['distribute_qty'] =0
                        vals.append(distribute_line)
            print vals
            for distribute_line in vals:
                    self.stock_distribution_lines_ids.create(distribute_line)
                     

    @api.multi
    @api.depends('received_qty', 'distribute_qty')
    def _get_remain_quntity(self):
        self.remain_qty=self.received_qty-self.distribute_qty
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('stock_distribution')
        res=super(inventory_distribution_to_shop, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        print ""
        res=super(inventory_distribution_to_shop, self).write(vals)
        
        return res
    
    @api.one
    def action_confirm(self):
        self.state = 'confirm'   
    @api.one
    def action_transfer(self):
        self.state = 'transfer'
        move_new_obj = self.pool['stock.move']
        
        stock_picking_hrd={}
        stock_picking_hrd['origin']=self.name
        stock_picking_hrd['picking_type_id']=1
        res=self.env['stock.picking'].create(stock_picking_hrd)
        for distribute_line in self.stock_distribution_lines_ids:
            if distribute_line.distribute_qty>0:
                print distribute_line.distribute_qty
                stock_move_order={}
                stock_move_order['picking_id']=res.id
                stock_move_order['product_id']=distribute_line.product_id.id
                stock_move_order['product_uom']=distribute_line.product_id.uom_id.id
                stock_move_order['name']=distribute_line.product_id.name
                stock_move_order['product_uom_qty']=distribute_line.distribute_qty
                stock_move_order['location_id']=distribute_line.source_location_id.id
                stock_move_order['location_dest_id']=distribute_line.target_location_id.id
                move_id = self.env['stock.move'].create(stock_move_order)
                
                move_new_obj.action_done(self.env.cr, self.env.uid, [move_id.id])
        
        
            
        
        

      
     
        