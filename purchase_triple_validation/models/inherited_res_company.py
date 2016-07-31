from openerp import api, exceptions, fields, models

class InheritedResCompany(models.Model):
    _inherit = 'res.company'
    
    po_double_validation = fields.Selection([
        ('one_step', 'Confirm purchase orders in one step'),
        ('two_step', 'Get 2 levels of approvals to confirm a purchase order'),
        ('three_step', 'Get 3 levels of approvals to confirm a purchase order')
        ], string="Levels of Approvals", default='one_step',\
        help="Provide a double or triple validation mechanism for purchases")
    
    po_triple_validation_amount = fields.Monetary(string='Triple validation amount', default=100000,\
        help="Minimum amount for which a triple validation is required")