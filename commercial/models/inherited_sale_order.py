from openerp import models, fields, api, exceptions

class InheritedSaleOrder(models.Model):
    """ Inherit Sale Order model """
    
    _inherit= 'sale.order'

    
    """ Relationship fields """
    sc_id = fields.Many2one('sales.contract')
