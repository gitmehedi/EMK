from openerp import api, exceptions, fields, models
from openerp import tools
from datetime import datetime

class EpoReservationStatus(models.Model):
    
    _name = 'epo.reservation.status.report'
    _auto = False
    

    id= fields.Integer('Product id')
    product_name= fields.Char('Product')
    quantity= fields.Float('Reserve Qty')
    location_name= fields.Char('Location')
    epo_no = fields.Char('EPO No')