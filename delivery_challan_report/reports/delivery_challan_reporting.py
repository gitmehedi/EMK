from odoo import api, fields, models, _
import datetime
import math


class DeliveryChallanReport(models.AbstractModel):
    _name = 'report.delivery_challan_report.report_top_sheet'

    @api.multi
    def render_html(self, docids, data=None):
        picking_obj = self.env['stock.picking'].browse(data.get('picking_id'))

        products = list()
        report_data = dict()

        for line in picking_obj.pack_operation_ids:
            product = dict()
            product['product_name'] = line.product_id.display_name
            product['uom_name'] = line.product_uom_id.name
            product['qty'] = line.qty_done
            product['qty_in_kg'] = product['qty'] * 1000 if product['uom_name'] == 'MT' else product['qty']
            products.append(product)

        report_data['so_name'] = picking_obj.delivery_order_id.sale_order_id.name
        report_data['so_date'] = picking_obj.delivery_order_id.sale_order_id.date_order
        report_data['note'] = picking_obj.note
        report_data['challan_no'] = picking_obj.name
        report_data['do_no'] = picking_obj.delivery_order_id.name
        report_data['do_date'] = picking_obj.date_done
        report_data['vehicle_no'] = picking_obj.vehicle_no

        bin_number = picking_obj.partner_id.bin

        if not picking_obj.customer_name:
            report_data['partner_name'] = picking_obj.partner_id.name
        else:
            report_data['partner_name'] = picking_obj.customer_name

        if bin_number:
            report_data['partner_name'] += ", BIN:" + bin_number

        if not picking_obj.shipping_address_print:
            report_data['shipping_address'] = self.get_address_by_partner(picking_obj.partner_id)
        else:
            report_data['shipping_address'] = picking_obj.shipping_address_print

        report_data['vat_challan_id'] = picking_obj.vat_challan_id
        report_data['challan_creation_system_date'] = datetime.datetime.today().strftime('%d-%m-%Y')

        docargs = {
            'data': report_data,
            'lists': products,
            'amount_to_word': self.amount_to_word,
        }

        return self.env['report'].render('delivery_challan_report.report_top_sheet', docargs)

    @api.multi
    def amount_to_word(self, value):
        return self.env['res.currency'].amount_to_word(float(value), False)

    def get_address_by_partner(self, partner):

        address = partner.address_get(['delivery', 'invoice'])
        delivery_address = self.env['res.partner'].browse(address['delivery'])

        address = []
        if delivery_address.street:
            address.append(delivery_address.street)

        if delivery_address.street2:
            address.append(delivery_address.street2)

        if delivery_address.zip_id:
            address.append(delivery_address.zip_id.name)

        if delivery_address.city:
            address.append(delivery_address.city)

        if delivery_address.state_id:
            address.append(delivery_address.state_id.name)

        if delivery_address.country_id:
            address.append(delivery_address.country_id.name)

        str_address = '\n '.join(address)

        return str_address
