from openerp import api, fields, models

class ProductStyleDocs(models.Model):
    _name = 'product.style.docs'
    
    title = fields.Char(string='File Title', required=True, size=30)
    file = fields.Binary("Image", help="Select file here")
    doc_id = fields.Many2one('product.style', ondelete="cascade")
    
    
    """ All functions """

    @api.model
    def create(self, vals):
        vals['title'] = vals.get('title', False).strip()
        
        return super(ProductStyleDocs, self).create(vals)
    
    @api.multi
    def write(self, vals):
        if vals.get('title', False):
            vals['title'] = vals.get('title', False).strip()
        
        return super(ProductStyleDocs, self).write(vals)
    
