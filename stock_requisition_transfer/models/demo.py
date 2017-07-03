import datetime

from openerp import api, models, fields, exceptions
from openerp.tools.translate import _
import time


class Demo(models.Model):
    """
    Send product to other shop
    """
    _name = 'demo'

    barcode = fields.Char(string='Product Barcode', size=15)
    counter = fields.Integer(string="Counter")

    @api.onchange('barcode')
    def _onchange_barcode(self):
        print "-------- Start the process --------"
        # if self.barcode:
        self.counter = self.counter + 1
        print "-------- before --------", self.counter
        # self.barcode = False
        print "-------- after --------", self.counter
