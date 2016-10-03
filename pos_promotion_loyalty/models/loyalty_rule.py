from openerp import models, fields
from lxml.html import FieldsDict
from gdata.contentforshopping.data import Year

class LoyaltyRule (models.Model):
    """
    Loyalty Rule
    """
    _name = 'loyalty.rule'
    
    # Mandatory and Optional Fields
    name = fields.Char(string = "Rule Name")
    is_active = fields.Boolean(string = "Active")
    loyalty_basis = fields.Selection([('purchase amount','Purchase Amount'), ('product category','Product Category')])
    min_purchase = fields.Float(string = "Minimum Purchase")
    purchase_unit_per_point = fields.Float(string = "Purchase Unit per Point")
    start_date = fields.Date(string = "Start Date")
    end_date = fields.Date(string = "End Date")
    point_unit = fields.Float(string = "Point Unit")
    
    # Relational Fields
    redemption_ids = fields.One2many('redemption.rule','loyalty_id',string = "Redemption Rule")
    
    