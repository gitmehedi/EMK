from odoo import models, fields, api, _
from odoo.addons.procurement.models import procurement
from odoo.tools.float_utils import float_round
from datetime import datetime
from odoo.exceptions import UserError

import math

class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    price_unit = fields.Float( string='Price Unit',compute="_calculate_price_unit", store=False,readonly=True)

    @api.multi
    def _calculate_price_unit(self):
        if self[0].picking_id.id:
            stock_pool = self.env['stock.picking'].search([('id', '=', self[0].picking_id.id)])
            for sp in stock_pool:
                if sp.delivery_order_id:
                    for ol in sp.delivery_order_id.sale_order_id.order_line:
                        self.price_unit = ol.price_unit



class InheritStockPicking(models.Model):
    _inherit = 'stock.picking'
    _order = 'id DESC'

    delivery_order_id = fields.Many2one('delivery.order', string='D.O No.', readonly=True)
    delivery_mode = fields.Selection([('cnf', 'C&F'), ('fob', 'FOB')],compute="_calculate_delivery_mode", store=False,
                                     string='Delivery Mode',readonly=True)
    vat_mode = fields.Selection([('vat', 'VAT'), ('non_vat', 'Non VAT')], string='Is VAT Applicable',
                                compute="_calculate_vat_mode", store=False,readonly=True)
    bonded_mode = fields.Selection([('bonded', 'Bonded'), ('non_bonded', 'Non Bonded')], readonly=True,
                                   compute="_calculate_bonded_mode", store=False,
                                   string='Is Bonded Applicable')
    lc_id = fields.Many2one('letter.credit', string='Number', readonly=True, compute="_calculate_lc_id", store=False)
    region_type = fields.Selection([('local', "Local"), ('foreign', "Foreign")], readonly=True, compute="_calculate_region_type",store=False)
    so_type = fields.Selection([
        ('cash', 'Cash'),
        ('credit_sales', 'Credit'),
        ('lc_sales', 'L/C'),
        ('tt_sales', 'TT'),
        ('contract_sales', 'Sales Contract'),
    ], string='Sales Type', readonly=True,compute="_calculate_so_type",store=False)
    expiry_date = fields.Date('Expiry Date',readonly=True,
                              compute="_calculate_expiry_date", store=False)
    shipment_date = fields.Date('Shipment Date',readonly=True,
                                compute="_calculate_shipment_date", store=False)
    issue_date = fields.Date('Date', readonly=True,
                             compute="_calculate_issue_date", store=False)
    bank_code = fields.Char(string='Bank',readonly=True,
                            compute="_calculate_bank_code", store=False)
    pack_type = fields.Many2one('product.packaging.mode', string='Packing Mode', readonly=True)
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
    min_date = fields.Datetime('Delivery Order Date', compute='_compute_dates', inverse='_set_min_date', store=True,
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

    customer_name = fields.Char(string='Partner (Print)',
                                states={'waiting': [('readonly', True)],
                                        'done': [('readonly', True)],
                                        'cancel': [('readonly', True)]})

    shipping_address_print = fields.Text(string='Address (Print)', states={ 'waiting': [('readonly', True)],
                                                                            'done': [('readonly', True)],
                                                                            'cancel': [('readonly', True)]})



    # Inherit Validate Button function
    @api.multi
    def do_new_transfer(self):
        user = self.env.user.browse(self.env.uid)
        # Check only for non admin user
        if user.has_group('base_technical_features.group_technical_features') == False:
            if self.so_type and self.so_type == 'lc_sales' and self.shipment_date and self.date_done:
                shipment_date = datetime.strptime(self.lc_id.shipment_date, '%Y-%m-%d').date()
                # date_done = datetime.strptime(self.date_done, '%Y-%m-%d %H:%M:%S').date()
                curr_date = datetime.now().date()
                if shipment_date < curr_date:
                    raise UserError(_("Unable to deliver Goods due to 'LC Shipment Date' Expired. Please contact to appropriate person for LC Shipment Date Amendment. After that you can deliver the Goods."))

        # check for available qty
        self._check_available_quantity()

        res = super(InheritStockPicking, self).do_new_transfer()

        self._get_number_of_jar()
        self._set_date_done_do()
        return res

    def _check_available_quantity(self):
        if self.picking_type_id.code == 'outgoing':
            for operation in self.pack_operation_product_ids:
                move = self.move_lines.filtered(lambda l: l.product_id.id == operation.product_id.id)
                on_hand_qty = move.availability + move.reserved_availability

                if operation.product_qty > on_hand_qty:
                    if operation.qty_done == 0 or operation.qty_done > on_hand_qty:
                        raise UserError(_("Unable to Deliver Goods due to qty is not available in current stock."))

    def _set_report_related_vals_to_move(self):
        pass

    def _get_number_of_jar(self):

        if self.pack_type.uom_id and not self.pack_type.is_jar_bill_included:
            for picking_line in self.pack_operation_product_ids:
                jar_count = (
                                picking_line.qty_done * picking_line.product_uom_id.factor_inv) / self.pack_type.uom_id.factor_inv

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

                #Update stock Move for reporting purpose
                self.move_lines.write({'packing_uom_id':self.pack_type.uom_id.id, 'jar_count':math.ceil(jar_count)})

    def _set_date_done_do(self):
        for move in self.move_lines:
            if move.undelivered_qty == 0.0:
                do_objs = self.env['delivery.order'].search([('id', '=', self.delivery_order_id.id)])
                do_line_objs = do_objs.line_ids.filtered(lambda x: x.product_id.id == move.product_id.id)
                if do_line_objs:
                    if self.date_done:
                        do_line_objs.date_done = self.date_done
                    else:
                        do_line_objs.date_done = fields.Datetime.now()

    @api.multi
    def _calculate_lc_id(self):
        for stock_lc in self:
            stock_lc.lc_id = stock_lc.delivery_order_id.sale_order_id.lc_id.id

    @api.multi
    def _calculate_region_type(self):
        for stock_picking in self:
            stock_picking.region_type = stock_picking.delivery_order_id.sale_order_id.region_type

    @api.multi
    def _calculate_so_type(self):
        for stock_picking in self:
            stock_picking.so_type = stock_picking.delivery_order_id.sale_order_id.type_id.sale_order_type

    @api.multi
    def _calculate_delivery_mode(self):
        for sp in self:
            sp.delivery_mode = sp.delivery_order_id.sale_order_id.delivery_mode

    @api.multi
    def _calculate_vat_mode(self):
        for sp in self:
            sp.vat_mode = sp.delivery_order_id.sale_order_id.vat_mode

    @api.multi
    def _calculate_bonded_mode(self):
        for sp in self:
            sp.bonded_mode = sp.delivery_order_id.sale_order_id.bonded_mode

    @api.multi
    def _calculate_expiry_date(self):
        for sp in self:
            sp.expiry_date = sp.delivery_order_id.sale_order_id.lc_id.expiry_date

    @api.multi
    def _calculate_issue_date(self):
        for sp in self:
            sp.issue_date = sp.delivery_order_id.sale_order_id.lc_id.issue_date

    @api.multi
    def _calculate_shipment_date(self):
        for sp in self:
            sp.shipment_date = sp.delivery_order_id.sale_order_id.lc_id.shipment_date

    @api.multi
    def _calculate_bank_code(self):
        for sp in self:
            sp.bank_code = sp.delivery_order_id.sale_order_id.lc_id.bank_code

    @api.multi
    def do_print_delivery_challan(self):

        data = {}
        data['picking_id'] = self.id
        return self.env["report"].get_action(self, 'delivery_challan_report.report_top_sheet', data)


class InheritStockMove(models.Model):
    _inherit = 'stock.move'

    # below 2 fields added for Delivery related reporting
    packing_uom_id = fields.Many2one('product.uom', string='Packing UoM ID')
    jar_count = fields.Float(string='# of Jar')

    delivery_order_id = fields.Many2one('delivery.order', string='D.O No.', readonly=True)

    undelivered_qty = fields.Float(
        'Undelivered Quantity', compute='_get_undelivered_qty',
        digits=0, states={'done': [('readonly', True)]}, store=True)

    @api.one
    @api.depends('linked_move_operation_ids.qty')
    def _get_undelivered_qty(self):
        self.undelivered_qty = float_round(
            self.product_qty - sum(self.mapped('linked_move_operation_ids').mapped('qty')),
            precision_rounding=self.product_id.uom_id.rounding)
