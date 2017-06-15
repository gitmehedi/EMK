from openerp import api, fields, models
from lxml import etree


class InheritedPosConfig(models.Model):
    _inherit= 'pos.config'

    active_shop = fields.Boolean(string='Active Shop', default=False)

      
     
        