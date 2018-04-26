from odoo import api, exceptions, fields, models

class MrrReport(models.AbstractModel):
    _name = 'report.gbs_purchase_order.report_purchase_order'

    @api.multi
    def render_html(self, docids, data=None):
        po_run_pool = self.env['purchase.order']
        docs = po_run_pool.browse(docids[0])
        report_utility_pool = self.env['report.utility']
        order_list = []
        total_amount = []
        address = []
        if docs.partner_id.street:
            address.append(docs.partner_id.street)

        if docs.partner_id.street2:
            address.append(docs.partner_id.street2)

        if docs.partner_id.zip_id:
            address.append(docs.partner_id.zip_id.name)

        if docs.partner_id.city:
            address.append(docs.partner_id.city)

        if docs.partner_id.state_id:
            address.append(docs.partner_id.state_id.name)

        if docs.partner_id.country_id:
            address.append(docs.partner_id.country_id.name)

        str_address = ' ,'.join(address)

        data = {}
        data['name'] = docs.name
        data['date_order'] = docs.date_order
        order_date = report_utility_pool.getERPDateFormat(report_utility_pool.getDateTimeFromStr(data['date_order']))
        data['partner_id'] = docs.partner_id.name
        data['address'] = str_address
        data['partner_ref'] = docs.partner_ref
        data['company'] = docs.operating_unit_id.partner_id.name
        data['notes'] = docs.notes
        data['company_address'] = docs.operating_unit_id.partner_id.street
        if docs.partner_id.child_ids:
            for con in docs.partner_id.child_ids[0]:
                data['sup_con'] = con.name
        else:
            data['sup_con']= ''

        if docs.order_line:
            for ol in docs.order_line:
                list_obj = {}
                list_obj['product_id']= ol.product_id.name
                list_obj['product_qty']= ol.product_qty
                list_obj['price_unit']= ol.price_unit
                list_obj['price_subtotal']= ol.price_subtotal
                total_amount.append(list_obj['price_subtotal'])
                order_list.append(list_obj)

        total = sum(total_amount)
        amt_to_word = self.env['res.currency'].amount_to_word(float(total))

        docargs = {
            'lists': order_list,
            'data': data,
            'total_amount': total,
            'amt_to_word': amt_to_word,
            'order_date': order_date
        }

        return self.env['report'].render('gbs_purchase_order.report_purchase_order', docargs)