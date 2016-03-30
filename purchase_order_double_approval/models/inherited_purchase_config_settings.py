from openerp import api, fields, models
from openerp import _
from openerp.exceptions import Warning

class InheritedPurchaseConfigSettings(models.Model):
	_inherit = 'purchase.config.settings'

	module_purchase_order_double_approval= fields.Boolean("Force three levels of approvals",
            help='Provide a double validation mechanism for purchases exceeding minimum amount and minimum item qty.\n'
                 '-This installs the module purchase_order_double_approval.')