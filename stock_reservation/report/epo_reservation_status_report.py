from openerp import api, exceptions, fields, models
from openerp import tools
from datetime import datetime

class EpoReservationStatus(models.Model):
    
    _name = 'epo.reservation.status.report'
    _auto = False
    
    id= fields.Integer('Sequence')
    product_id= fields.Integer('Product id')
    name= fields.Char('Product')
    quantity= fields.Float('Qty')
    location_name= fields.Char('Location')
    epo_no = fields.Char('EPO No')