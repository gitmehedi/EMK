from odoo import tools
from odoo import models, fields, api


class JarSummaryAnalyticReport(models.Model):
    _name = "jar.summary.analytic.report"
    _description = "JAR Summary Analytic Report"
    _auto = False
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)], required=True)
    total_jar_taken = fields.Integer(string='Total Jar Taken')
    jar_received = fields.Integer(string='Jar Received')
    jar_received_date = fields.Datetime(string='Jar Received Date')
    uom_id = fields.Many2one('product.uom', string='UoM')
    due_jar = fields.Integer(string='Due Jar', compute='_calculate_number_of_due_jar')


    @api.multi
    def _calculate_number_of_due_jar(self):
        for jar in self:
            jar.due_jar = jar.total_jar_taken - jar.jar_received


    _order = 'jar_received_date desc'


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
               SELECT * FROM uom_jar_summary)""" % (self._table))
