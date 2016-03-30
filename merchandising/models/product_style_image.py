from openerp import api, fields, models
from openerp.addons.helper import validator

class ProductStyleImage(models.Model):
    _name = 'product.style.image'
    
    title = fields.Char(string='Image Title (Please provide JPG,JEPG,PNG or GIF)', required=True, size=30)
    image = fields.Binary("Image", help="Select image here")
    style_id = fields.Many2one('product.style', ondelete="cascade")
    
    
    # All functions
    
    @api.multi
    def _validate_data(self, value):
        msg , filterChar = {}, {}
        
        filterChar['Image Title'] = value.get('title', False)
        
        msg.update(validator._validate_character(filterChar, True))
        validator.validation_msg(msg)
        
        return True
    
    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        vals['title'] = vals.get('title', False).strip()
        
        return super(ProductStyleImage, self).create(vals)
    
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        
        if vals.get('title', False):
            vals['title'] = vals.get('title', False).strip()
        
        return super(ProductStyleImage, self).write(vals)
    
