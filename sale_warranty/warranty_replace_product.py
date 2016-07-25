from openerp.osv import fields, osv

class warranty_replace_product(osv.osv):
    
    _name = 'warranty.replace.product'
    _description = "Warranty Replaced Products"
    
    _columns = {
          'name':fields.char('Ref No', required=True),
          'replaced_date':fields.date('Date of Sale', required=True),
          'dealer_id':fields.many2one('res.partner', 'Dealer', required=True),
          'user_id': fields.many2one('res.users', 'Users', required=True),
          'product_id':fields.many2one('product.product', 'Product', required=True),
          'claim_id': fields.many2one('sale.warranty.claim', string='Claim'),
          'warranty_id': fields.related('claim_id', 'warranty_id', relation='sale.warranty', 
                                        type='many2one', string='Claim'), 
          'batch_no':fields.char('Batch No', required=True),
          'model':fields.char('Model'),
    }
    
warranty_replace_product()