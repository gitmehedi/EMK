from odoo import api, fields, models
import time, datetime


class ProcessDateWiseSchedule(models.Model):
    _name = 'delivery.schedule.date.wise'
    _description = 'Delivery Schedule Date Wise'
    _order = "id DESC"

    partner_id = fields.Many2one('res.partner', 'Customer', domain="([('customer','=','True')])", readonly=True)
    pending_do = fields.Many2one('stock.picking', string='Pending D.O', readonly=True)
    do_qty = fields.Float(string='Ordered Qty', readonly=True)
    undelivered_qty = fields.Float(string='Undelivered Qty', readonly=True)
    uom_id = fields.Many2one('product.uom', string="Unit of Measure", readonly=True)
    scheduled_qty = fields.Float(string='Scheduled Qty.', readonly=True)
    remarks = fields.Text('Special Instructions', readonly=True)
