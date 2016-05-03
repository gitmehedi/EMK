from openerp import api, exceptions, fields, models
from openerp.addons.helper import validator

class IndentProductLines(models.Model):
    _name = 'indent.product.lines'
    _description = 'Indent Product Lines'
    
    
    def _get_indent_type_gen_flag_value(self):
        if self._context.get('indent_type', False) == "gen":
            return True
        else:
            return False
    
#     def _get_indent_type_bom_flag_value(self):
#         if self._context.get('indent_type', False) == "bom":
#             return True
#         else:
#             return False
        
    indent_id = fields.Many2one('indent.indent', 'Indent', required=True, ondelete='cascade')
    
    #@api.model
#     def _get_indent_type(self):
#         print "self ", self.indent_id.type
#         res = {}
#         for line in self:
#             print 'type ',line.indent_id.type
#             
#             if(line.indent_id.type=="new"):
#                 ids = self.env['product.product'].search([['type', '!=', 'service']])
#                 res.update(domain={
#                     'self.product_id': ['id', 'in', [rec.id for rec in ids]]
#                 })
#             elif(line.indent_id.type == "existing"):
#                 ids = self.env['product.product'].search([['type', '=', 'service']])
#                 res.update(domain={
#                     'self.product_id': ['id', 'in', [rec.id for rec in ids]]
#                 })
#             print 'res ',res
#         return res
#     
# 
#     _defaults = {      
#             'product_id': _get_indent_type,
#      }
    product_id = fields.Many2one('product.product', 'Product', required=True)
    original_product_id = fields.Many2one('product.product', 'Product to be Repaired')
    type = fields.Selection([('make_to_stock', 'Stock'), ('make_to_order', 'Purchase')], 'Procure', required=True,
     help="From stock: When needed, the product is taken from the stock or we wait for replenishment.\nOn order: When needed, the product is purchased or produced.")
    product_uom_qty = fields.Float('Quantity Required', digits=(14, 2), required=True)
    product_uom = fields.Many2one('product.uom', 'Unit of Measure', required=True)
    product_uos_qty = fields.Float('Quantity (UoS)' ,digits=(14, 2))
    product_uos = fields.Many2one('product.uom', 'Product UoS')
    price_unit = fields.Float('Price', required=True, digits=(20, 4),  help="Price computed based on the last purchase order approved.")
    #price_subtotal = fields.Float(string='Subtotal', digits=(20, 4),  compute='_amount_subtotal',  store=True)
    price_subtotal = fields.Float(digits=(20, 4), compute='_compute_subtotal', string='Subtotal', store=True)
    qty_available = fields.Float('In Stock')
    virtual_available = fields.Float('Forecasted Qty')
    delay = fields.Float('Lead Time', required=True)
    name = fields.Char('Purpose', size=255, required=True)
    specification = fields.Text('Specification')
    sequence = fields.Integer('Sequence')
    indent_type = fields.Selection([('new', 'Purchase Indent'), ('existing', 'Repairing Indent')], 'Type')
    required_date= fields.Date('Required Date',default=fields.Date.today(), required=True)
    indent_type_gen_flag = fields.Boolean(default=_get_indent_type_gen_flag_value)
#     indent_type_bom_flag = fields.Boolean(default=_get_indent_type_bom_flag_value)
    #indent_type = fields.Char('Type', required=True, related="indent_id.type")
    """
    def _amount_subtotal(self, cr, uid, ids, name, args, context=None):
        result = {}
        for line in self.browse(cr, uid, ids, context=context):
            result[line.id] = (line.product_uom_qty * line.price_unit)
        return result
    """
    
    
    
    def _get_uom_id(self, cr, uid, *args):
        result = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'product', 'product_uom_unit')
        return result and result[1] or False
    
    def _get_default_type(self, cr, uid, *args):
        context = args[0]
        return context.get('indent_type')
    
    _defaults = {
        'product_uom_qty': 1,
        'product_uos_qty': 1,
        'type': 'make_to_order',
        'delay': 0.0,
        'indent_type':_get_default_type,
        #'sequence': lambda self: self.env['ir.sequence'].get('sequence'),
    }
    
    
    @api.multi
    def _validate_data(self, value):
        msg , filterInt = {}, {}
        
        filterInt['Quantity'] = value.get('product_uom_qty', False)
        filterInt['Price'] = value.get('price_unit', False)
       
        msg.update(validator._validate_number(filterInt))
        validator.validation_msg(msg)
        
        return True
            

        
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        return super(IndentProductLines, self).create(vals)
   
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        return super(IndentProductLines, self).write(vals)
    
    def _check_stock_available(self, cr, uid, ids, context=None):
#         for move in self.browse(cr, uid, ids, context):
#             if move.type == 'make_to_stock' and move.product_uom_qty > move.qty_available:
#                 return False
        return True
    
    _constraints = [
        (_check_stock_available, 'You can not procure more quantity form stock then the available !.', ['Quantity Required']),
    ]
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        pro_obj=self.env["product.product"]
        uom_obj = self.env["product.uom"]
        if self.product_id.id:
            uom_ins = pro_obj.browse([self.product_id.id])
            self.product_uom=uom_ins.uom_id.id
            self.price_unit = self.product_id.standard_price
            self.qty_available = self.product_id.qty_available
            self.virtual_available = self.product_id.virtual_available
            self.name = self.product_id.name
        if self._context.get('required_date', False):
            self.required_date = self._context.get('required_date', False)
    
    @api.onchange('product_uom_qty','price_unit')
    def onchange_product_qty_price(self):
        if self.product_uom_qty > 0:
            self.price_subtotal = self.product_uom_qty * self.price_unit 
    
    @api.multi
    @api.depends('product_uom_qty', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            if line.product_uom_qty > 0:
                line.price_subtotal = line.product_uom_qty * line.price_unit 
                if line.price_subtotal > 0:
                    line.indent_id.amount_flag = True

    """
    def onchange_product_id(self, cr, uid, ids, product_id=False, product_uom_qty=0.0, product_uom=False, price_unit=0.0, qty_available=0.0, virtual_available=0.0, name='', analytic_account_id=False, indent_type=False, context=None):
        result = {}
        product_obj = self.pool.get('product.product')
        if not product_id:
            return {'value': {'product_uom_qty': 1.0, 'product_uom': False, 'price_unit': 0.0, 'qty_available': 0.0, 'virtual_available': 0.0, 'name': '', 'delay': 0.0}}

        product = product_obj.browse(cr, uid, product_id, context=context)        
        
        if product.qty_available > 0:
            result['type'] = 'make_to_stock'
        else:
            result['type'] = 'make_to_order'
        
        result['name'] = product_obj.name_get(cr, uid, [product.id])[0][1]
        result['product_uom'] = product.uom_id.id
        result['price_unit'] = product.standard_price
        result['qty_available'] = product.qty_available
        result['virtual_available'] = product.virtual_available        
        result['specification'] = product_obj.name_get(cr, uid, [product.id])[0][1]
        
        if product.type == 'service':
            result['original_product_id'] = product.repair_id.id
            result['type'] = 'make_to_order'
        else:
            result['original_product_id'] = False
            
        #You must define at least one supplier for this product
        if not product.seller_ids:
            user = self.pool.get('res.users').browse(cr, uid, uid)
            result['delay'] = user.company_id.po_lead or 0
            #raise osv.except_osv(_("Warning !"), _("You must define at least one supplier for this product"))
        else:
            result['delay'] = product.seller_ids[0].delay
        
        return {'value': result}
    """