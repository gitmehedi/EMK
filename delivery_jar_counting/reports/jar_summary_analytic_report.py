from odoo import tools
from odoo import models, fields, api
import time, datetime


class JarSummaryAnalyticReport(models.Model):
    _name = "jar.summary.analytic.report"
    _description = "JAR Summary Analytic Report"
    _auto = False
    _rec_name = 'partner_id'

    #product_id = fields.Many2one('product.product', string='Product')
    #jar_type = fields.Char(string='Jar Type')
    #uom_id = fields.Many2one('product.uom', string='UoM')
    #challan_id = fields.Many2one('stock.picking', string='Challan Id')
    partner_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)], required=True)
    due_jar = fields.Integer(string='# of Due Jar')
    # due_jar = fields.Integer(string='Due Jar till today', readonly=False)
    jar_received = fields.Integer(string='# Jar Received')
    packing_name = fields.Char(string='Packing Name')
    date = fields.Date('Date')

    # due_jar = fields.Integer(string='Due Jar till today', readonly=False, track_visibility='onchange')
    # jar_received = fields.Integer(string='# Jar Received', )


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
          SELECT id,DATE(create_date),due_jar,jar_received,partner_id,packing_mode,packing_name
              FROM jar_received 
              WHERE state = 'confirmed'             
               
               )""" % (self._table))
