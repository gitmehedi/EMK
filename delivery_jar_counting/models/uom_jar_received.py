from odoo import api, fields, models
import datetime


class UomJarSummary(models.Model):
    _name = 'uom.jar.received'
    _description = 'UoM JAR Received'
    _rec_name = 'partner_id'


    partner_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)], required=True)
    due_jar = fields.Integer(string='Due Jar', readonly=False)
    jar_received = fields.Integer(string='# Jar Received')
    challan_id = fields.Many2one('stock.picking', string='Challan Id', domain=[('state','=','assigned')])

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
    ], default='draft')

    @api.onchange('partner_id')
    def _partner_id_onchange(self):
        stock_picking_obj = self.env['stock.picking'].search([('partner_id', '=', self.partner_id.id)])

        total_qty = 0
        for cust in stock_picking_obj:
            if cust.sale_id.pack_type.is_jar_bill_included:
                total_qty += cust.move_lines.product_uom_qty

        self.total_jar_taken = total_qty

        jar_summ_obj = self.env['uom.jar.summary'].search([('partner_id', '=', self.partner_id.id)])
        for summ in jar_summ_obj:
            self.due_jar = self.total_jar_taken - summ.jar_received

    def action_confirm(self):
        jar_summ_obj = self.env['uom.jar.summary'].search([('partner_id', '=', self.partner_id.id)])
        for summ in jar_summ_obj:
            if summ:
                summ.write(
                    {
                        'jar_received': self.jar_received,
                        'jar_received_date': datetime.datetime.now()

                    })

        self.state = 'confirmed'
