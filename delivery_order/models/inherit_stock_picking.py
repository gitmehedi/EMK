from odoo import models, fields, api
from odoo.addons.procurement.models import procurement
from odoo.tools.float_utils import float_round
import time, datetime


import math


class InheritStockPicking(models.Model):
    _inherit = 'stock.picking'

    delivery_order_id = fields.Many2one('delivery.order', string='D.O No.', readonly=True)

    pack_type = fields.Many2one('product.packaging.mode', string='Packing Mode', readonly=True)

    lc_id = fields.Many2one('letter.credit', string='L/C No', readonly=True, compute="_calculate_lc_id", store=False)

    show_transport_info = fields.Boolean(string='Show Transport Info', default=False,
                                         states={'partially_available': [('readonly', True)],
                                                 'confirmed': [('readonly', True)], 'waiting': [('readonly', True)],
                                                 'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    vat_challan_id = fields.Char(string='VAT Challan Id', states={'partially_available': [('readonly', True)],
                                                                  'confirmed': [('readonly', True)],
                                                                  'waiting': [('readonly', True)],
                                                                  'done': [('readonly', True)],
                                                                  'cancel': [('readonly', True)]},
                                 track_visibility='onchange')

    transport_details = fields.Selection([
        ('owned', 'Owned'),
        ('hired', 'Hired'),
    ], string='Type', states={'partially_available': [('readonly', True)],
                              'confirmed': [('readonly', True)], 'waiting': [('readonly', True)],
                              'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    transport_name = fields.Text(string='Transport Details',
                                 states={'partially_available': [('readonly', True)],
                                         'confirmed': [('readonly', True)], 'waiting': [('readonly', True)],
                                         'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    vehicle_no = fields.Char(size=100, string='Vehicle #',
                             states={'partially_available': [('readonly', True)],
                                     'confirmed': [('readonly', True)], 'waiting': [('readonly', True)],
                                     'done': [('readonly', True)], 'cancel': [('readonly', True)]},
                             track_visibility='onchange')
    driver_no = fields.Char(size=100, string='Driver Name',
                            states={'partially_available': [('readonly', True)],
                                    'confirmed': [('readonly', True)], 'waiting': [('readonly', True)],
                                    'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    driver_mob = fields.Char(size=100, string='Driver Mob #',
                             states={'partially_available': [('readonly', True)],
                                     'confirmed': [('readonly', True)], 'waiting': [('readonly', True)],
                                     'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    # Inherited below fields to meet custom demands
    partner_id = fields.Many2one('res.partner', 'Partner',
                                 states={'assigned': [('readonly', True)], 'partially_available': [('readonly', True)],
                                         'confirmed': [('readonly', True)], 'waiting': [('readonly', True)],
                                         'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    min_date = fields.Datetime('Scheduled Date', compute='_compute_dates', inverse='_set_min_date', store=True,
                               index=True, track_visibility='onchange',
                               states={'assigned': [('readonly', True)], 'partially_available': [('readonly', True)],
                                       'confirmed': [('readonly', True)], 'waiting': [('readonly', True)],
                                       'done': [('readonly', True)], 'cancel': [('readonly', True)]},
                               help="Scheduled time for the first part of the shipment to be processed. Setting manually a value here would set it as expected date for all the stock moves.")

    origin = fields.Char('Source Document', index=True,
                         states={'assigned': [('readonly', True)], 'partially_available': [('readonly', True)],
                                 'confirmed': [('readonly', True)], 'waiting': [('readonly', True)],
                                 'done': [('readonly', True)],
                                 'cancel': [('readonly', True)]},
                         help="Reference of the document")

    move_type = fields.Selection([
        ('direct', 'Partial'), ('one', 'All at once')], 'Delivery Type',
        default='direct', required=True,
        states={'assigned': [('readonly', True)], 'partially_available': [('readonly', True)],
                'confirmed': [('readonly', True)], 'waiting': [('readonly', True)], 'done': [('readonly', True)],
                'cancel': [('readonly', True)]},
        help="It specifies goods to be deliver partially or all at once")

    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Picking Type',
        required=True, states={'assigned': [('readonly', True)], 'partially_available': [('readonly', True)],
                               'confirmed': [('readonly', True)], 'waiting': [('readonly', True)],
                               'done': [('readonly', True)],
                               'cancel': [('readonly', True)]}, )

    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get('stock.picking'),
        index=True, required=True,
        states={'assigned': [('readonly', True)],
                'partially_available': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'waiting': [('readonly', True)],
                'done': [('readonly', True)],
                'cancel': [('readonly', True)]})

    operating_unit_id = fields.Many2one('operating.unit',
                                        'Requesting Operating Unit', states={'assigned': [('readonly', True)],
                                                                             'partially_available': [
                                                                                 ('readonly', True)],
                                                                             'confirmed': [('readonly', True)],
                                                                             'waiting': [('readonly', True)],
                                                                             'done': [('readonly', True)],
                                                                             'cancel': [('readonly', True)]})

    priority = fields.Selection(
        procurement.PROCUREMENT_PRIORITIES, string='Priority',
        compute='_compute_priority', inverse='_set_priority', store=True,
        # default='1', required=True,  # TDE: required, depending on moves ? strange
        index=True, track_visibility='onchange',
        states={'assigned': [('readonly', True)],
                'partially_available': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'waiting': [('readonly', True)],
                'done': [('readonly', True)],
                'cancel': [('readonly', True)]},
        help="Priority for this picking. Setting manually a value here would set it as priority for all the moves")


    # Inherit Validate Button function
    @api.multi
    def do_new_transfer(self):
        res = super(InheritStockPicking, self).do_new_transfer()

        self._get_number_of_jar()
        self._set_date_done_do()
        return res


    def _get_number_of_jar(self):

        if self.pack_type.uom_id and not self.pack_type.is_jar_bill_included:
            for picking_line in self.pack_operation_product_ids:
                jar_count = (picking_line.qty_done * picking_line.product_uom_id.factor_inv) / self.pack_type.uom_id.factor_inv

                delivery_jar_count_obj = self.env['delivery.jar.count']

                vals = {}
                vals['partner_id'] = self.partner_id.id
                vals['product_id'] = picking_line.product_id.id
                vals['challan_id'] = self.id
                vals['uom_id'] = picking_line.product_uom_id.id
                vals['jar_count'] = math.ceil(jar_count)
                vals['packing_mode_id'] = self.pack_type.id
                vals['jar_type'] = self.pack_type.uom_id.display_name.upper().strip()
                vals['date'] = datetime.datetime.now().date()

                delivery_jar_count_obj.create(vals)

    def _set_date_done_do(self):
        for move in self.move_lines:
            if move.undelivered_qty == 0.0:
                do_objs = self.env['delivery.order'].search([('id','=',move.delivery_order_id.id)])
                do_line_objs = do_objs.line_ids.filtered(lambda x: x.product_id.id == move.product_id.id)
                if self.date_done:
                    do_line_objs.date_done = self.date_done
                else:
                    do_line_objs.date_done = fields.Datetime.now()

    @api.multi
    def _calculate_lc_id(self):
        for stock_lc in self:
            stock_lc.lc_id = stock_lc.delivery_order_id.sale_order_id.lc_id.id

    @api.multi
    def do_print_delivery_challan(self):
        return self.env["report"].get_action(self, 'delivery_challan_report.report_delivery_cha')


class InheritStockMove(models.Model):
    _inherit = 'stock.move'

    #below 2 fields added for Delivery related reporting
    packing_uom_id = fields.Many2one('product.uom', string='Packing UoM ID')
    jar_count = fields.Float(string='# of Jar')

    delivery_order_id = fields.Many2one('delivery.order', string='D.O No.', readonly=True)

    undelivered_qty = fields.Float(
        'Undelivered Quantity', compute='_get_undelivered_qty',
        digits=0, states={'done': [('readonly', True)]},store=True)

    @api.one
    @api.depends('linked_move_operation_ids.qty')
    def _get_undelivered_qty(self):
        self.undelivered_qty = float_round(self.product_qty - sum(self.mapped('linked_move_operation_ids').mapped('qty')),
                                         precision_rounding=self.product_id.uom_id.rounding)