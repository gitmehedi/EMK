from odoo import api, fields, models
import datetime


class UomJarSummary(models.Model):
    _name = 'uom.jar.summary'
    _rec_name = 'partner_id'
    _description = 'UoM JAR Summary'

    total_jar_taken = fields.Integer(string='Total Jar Taken')
    jar_received = fields.Integer(string='Jar Received')
    jar_received_date = fields.Datetime(string='Jar Received Date')

    partner_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)], required=True)
    uom_id = fields.Many2one('product.uom', string='UoM')
    due_jar = fields.Integer(string='Due Jar', compute='_calculate_number_of_due_jar')


    @api.model
    def _calculate_number_of_due_jar(self):
        for jar in self:
            jar.due_jar = jar.total_jar_taken - jar.jar_received


    @api.onchange('partner_id')
    def onchange_partner_id(self):

        stock_picking_obj = self.env['stock.picking'].search([('partner_id', '=', self.partner_id.id)])

        total_qty = 0
        for cust in stock_picking_obj:
            if cust.sale_id.pack_type.is_jar_bill_included:
                total_qty += cust.move_lines.product_uom_qty
                self.uom_id = cust.move_lines.product_uom

        self.total_jar_taken = total_qty

        jar_summ_obj = self.env['uom.jar.summary'].search([('partner_id', '=', self.partner_id.id)])
        for summ in jar_summ_obj:
            if summ:
                self.due_jar = self.total_jar_taken - summ.jar_received
                self.jar_received = summ.jar_received
