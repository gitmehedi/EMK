from openerp import api, fields, models

class InheritedPurchaseConfigureSettings(models.Model):
	_inherit = 'purchase.config.settings'

	module_purchase_triple_validation= fields.Boolean("Force three levels of approvals",
            help='Provide a double validation mechanism for purchases exceeding minimum amount and minimum item qty.\n'
                 '-This installs the module purchase_order_double_approval.')