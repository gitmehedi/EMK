from odoo import api, fields, models
import time

from datetime import date, datetime


class PartnerWiseJarSummary(models.AbstractModel):
    _name = 'report.gbs_sales_jar_count.report_jar_summary'

    @api.model
    def render_html(self, docids, data=None):

        data_list = []



        if data['partner_id']:

            uom_summary = self.env['uom.jar.summary'].search([('partner_id', '=', data['partner_id'])])

            for jars in uom_summary:
                vals = {}
                partner_id = jars.env['res.partner'].search([('id', '=', data['partner_id'])])

                vals['partner_id'] = partner_id.name
                vals['total_jar_taken'] = jars.total_jar_taken
                vals['jar_received'] = jars.jar_received
                vals['jar_received_date'] = jars.jar_received_date
                vals['uom_id'] = jars.uom_id[0].name
                vals['due_jar'] = jars.due_jar

                data_list.append(vals)

        else:
            uom_summary = self.env['uom.jar.summary'].search([])

            for all_cust in uom_summary:
                val = {}
                val['partner_id'] = all_cust.partner_id.name
                val['total_jar_taken'] = all_cust.total_jar_taken
                val['jar_received'] = all_cust.jar_received
                val['jar_received_date'] = all_cust.jar_received_date
                val['uom_id'] = all_cust.uom_id.name
                val['due_jar'] = all_cust.due_jar

                data_list.append(val)

        docargs = \
            {
                'data_list': data_list,
            }

        return self.env['report'].render('gbs_sales_jar_count.report_jar_summary', docargs)
