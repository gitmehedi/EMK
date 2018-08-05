from odoo import tools
from odoo import models, fields, api


class JarSummaryAnalyticReport(models.Model):
    _name = "jar.summary.analytic.report"
    _description = "JAR Summary Analytic Report"
    _auto = False
    _rec_name = 'partner_id'

    product_id = fields.Many2one('product.product', string='Product')
    jar_type = fields.Char(string='Jar Type')
    uom_id = fields.Many2one('product.uom', string='UoM')
    challan_id = fields.Many2one('stock.picking', string='Challan Id')
    partner_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)], required=True)
    jar_count = fields.Integer(string='# of Jar')
    #due_jar = fields.Integer(string='Due Jar till today', readonly=False)
    jar_received = fields.Integer(string='# Jar Received')

    # due_jar = fields.Integer(string='Due Jar till today', readonly=False, track_visibility='onchange')
    # jar_received = fields.Integer(string='# Jar Received', )

    # packing_mode = fields.Many2one('product.packaging.mode', string='Jar Type',
    #                                domain=[('is_jar_bill_included', '=', False)])

    # @api.multi
    # def _calculate_number_of_due_jar(self):
    #
    #
    #
    #     for jar in self:
    #         jar.due_jar = jar.total_jar_taken - jar.jar_received



    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (

SELECT j_rcv.id,d_jar.product_id,d_jar.jar_type, d_jar.uom_id, d_jar.challan_id, d_jar.partner_id, d_jar.jar_count, 
--d_jar.jar_count - j_rcv.jar_received AS DUE, 
j_rcv.jar_received,j_rcv.create_date
   FROM delivery_jar_count d_jar 
	 JOIN jar_received j_rcv ON
		d_jar.partner_id = j_rcv.partner_id
		WHERE d_jar.packing_mode_id = j_rcv.packing_mode ORDER BY d_jar.product_id
               
               
               )""" % (self._table))
