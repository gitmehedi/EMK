from openerp import models, fields
from lxml.html import FieldsDict
#from gdata.contentforshopping.data import Year

class RedemptionRule (models.Model):
    """
    Redemption Rule
    """
    _name = 'redemption.rule'
    
    # Mandatory and Optional Fields
    redemption_rule_name = fields.Char(string="Rule Name")
    reward_point_unit = fields.Float(string="Reward Point Unit")
    point_start_margin = fields.Float()
    point_end_margin = fields.Float()
    is_active = fields.Boolean(string="Active")
    
    # Relational FieldsDict
    loyalty_id = fields.Many2one('loyalty.rule', ondelete="cascade")
