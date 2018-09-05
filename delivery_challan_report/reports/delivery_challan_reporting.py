from odoo import api, fields, models, _
import datetime
import math


class DeliveryChallanReport(models.AbstractModel):
    _name = 'report.delivery_challan_report.report_top_sheet'


    @api.multi
    def render_html(self, docids, data=None):
        picking_obj = self.env['stock.picking'].browse(data.get('picking_id'))

        #Jar Count
        jar_count = None
        jar_type = None

        if picking_obj.pack_type.uom_id and not picking_obj.pack_type.is_jar_bill_included:
            for picking_line in picking_obj.pack_operation_product_ids:
                jar_count = (picking_line.qty_done * picking_line.product_uom_id.factor_inv) / picking_obj.pack_type.uom_id.factor_inv

                jar_count = math.ceil(jar_count)
                jar_type = picking_obj.pack_type.uom_id.display_name.upper().strip()

        else:
            jar_type = picking_obj.pack_type.display_name


        doc_list = []
        datas = {}
        for line in picking_obj.pack_operation_ids:
            vals = {}
            vals['product_id'] = line.product_id.display_name

            number_to_words = self.env['res.currency'].amount_to_word(float(line.qty_done),False)
            vals['number_to_words'] = number_to_words
            vals['uom'] = line.product_uom_id.name
            vals['quantity'] = line.qty_done
            vals['jar_count'] = jar_count
            vals['jar_type'] = jar_type

            doc_list.append(vals)


        datas['challan_no'] = picking_obj.name
        datas['do_no'] = picking_obj.delivery_order_id.name
        datas['do_date'] = picking_obj.date_done
        datas['vehicle_no'] = picking_obj.vehicle_no

        if not picking_obj.customer_name:
            datas['partner_id'] = picking_obj.partner_id.name

        else:
            datas['partner_id'] = picking_obj.customer_name


        if not picking_obj.shipping_address_print:
            datas['shipping_address'] = self.getAddressByPartner(picking_obj.partner_id)
        else:
            datas['shipping_address'] = picking_obj.shipping_address_print

        datas['vat_challan_id'] = picking_obj.vat_challan_id
        datas['challan_creation_system_date'] = datetime.datetime.today().strftime('%d-%m-%Y')

        docargs = {
            'data': datas,
            'lists': doc_list,
        }

        return self.env['report'].render('delivery_challan_report.report_top_sheet', docargs)


    def getAddressByPartner(self, partner):

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