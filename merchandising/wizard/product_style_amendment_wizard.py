from openerp import api, exceptions, fields, models
from openerp.addons.helper import validator
from validate import Validator
from duplicity.tempdir import default

class ProductStyleAmendmentWizard(models.TransientModel):
    """
    Product Style Amendment Wizard
    """
    _name = "product.style.wizard"
    
      
    # create a function that will save the info from your wizard into your model (active_id is the id of the record you called the wizard from, so you will save the info entered in wizard is that record)
    
    @api.multi
    def amaendment_copy(self, context=None):
        
        p_style = self.env['product.style'].browse(context['active_id'])
        res = p_style.copy_style(context)
        
        
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'src_model': 'product.style',
            'res_model': 'product.style',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': res.id
        }
       
       
