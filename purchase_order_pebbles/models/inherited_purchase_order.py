from openerp import api, fields, models
import pytz
from openerp import SUPERUSER_ID, workflow
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import attrgetter
from openerp.tools.safe_eval import safe_eval as eval
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.osv.orm import browse_record_list, browse_record, browse_null
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
from openerp.tools.float_utils import float_compare

class InheritedPurchaseOrder(models.Model):
	_inherit = 'purchase.order'
	



	def action_picking_create(self, cr, uid, ids, context=None):
		
		print "#################self#########################", self
# 		raise osv.except_osv(_('Error!'),_('You Line cannot confirm a purchase order without any purchase order line.'))
		return True

	def action_invoice_create(self, cr, uid, ids, context=None):
		"""Generates invoice for given ids of purchase orders and links that invoice ID to purchase order.
		:param ids: list of ids of purchase orders.
		:return: ID of created invoice.
		:rtype: int
		"""

	def action_purchase_done(self, cr, uid, ids, context=None):

		self.write(cr, uid, ids, {'state': 'done'}, context=context)
		

