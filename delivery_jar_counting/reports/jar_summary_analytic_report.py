from odoo import tools
from odoo import models, fields, api
import time, datetime


class JarSummaryAnalyticReport(models.Model):
    _name = "jar.summary.analytic.report"
    _description = "JAR Summary Analytic Report"
    _auto = False
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)], required=True)
    jar_type = fields.Char(string='Jar Type')
    qty1 = fields.Integer(string='# of Due Jar')
    qty2 = fields.Integer(string='# Jar Received')


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
                    SELECT
                      t1.id,
                      t1.partner_id AS partner_id,
                      t1.jar_type AS jar_type,
                      t1.qty1 AS qty1,
                      t2.qty2 AS qty2
                    FROM (SELECT
                      id,
                      partner_id,
                      jar_type,
                      SUM(jar_count) AS qty1
                    FROM delivery_jar_count
                    GROUP BY partner_id,jar_type,id) t1
                    LEFT JOIN (SELECT
                      id,
                      partner_id,
                      jar_type,
                      SUM(jar_received) AS qty2
                    FROM jar_received
                    GROUP BY partner_id,
                             jar_type,
                             id) t2
                      ON t1.partner_id = t2.partner_id
                      AND t1.jar_type = t2.jar_type)""" % (self._table))

