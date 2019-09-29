from odoo import api, exceptions, fields, models
from odoo.tools.misc import formatLang


class GbsPurchaseOrder(models.AbstractModel):
    _name = 'report.gbs_purchase_order.report_purchase_order'

    @api.multi
    def render_html(self, docids, data=None):
        po_run_pool = self.env['purchase.order']
        docs = po_run_pool.browse(docids[0])
        report_utility_pool = self.env['report.utility']
        order_list = []
        total_amount = []

        data = {}
        data['name'] = docs.name
        data['date_order'] = docs.date_order
        order_date = report_utility_pool.getERPDateFormat(report_utility_pool.getDateTimeFromStr(data['date_order']))
        requisition_date = report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(docs.requisition_id.requisition_date))
        data['partner_id'] = docs.partner_id.name
        data['cus_address'] = report_utility_pool.getCoustomerAddress(docs.partner_id)
        data['partner_ref'] = docs.partner_ref
        data['requisition_id'] = docs.requisition_id.name
        data['requisition_date'] = requisition_date
        # data['company'] = docs.operating_unit_id.partner_id.name
        data['company'] = docs.company_id.partner_id.name
        data['notes'] = docs.notes
        data['company_address'] = report_utility_pool.getCoustomerAddress(docs.operating_unit_id.partner_id)
        data['region_type'] = docs.region_type
        data['amount_vat'] = docs.amount_vat
        data['amount_discount'] = docs.amount_discount
        data['amount_after_discount'] = formatLang(self.env, docs.amount_after_discount)
        data['amount_total'] = formatLang(self.env,docs.amount_total)
        data['terms_condition'] = docs.terms_condition
        data['total_discount'] = docs.amount_untaxed * (docs.amount_discount / 100)
        data['total_vat'] = docs.amount_after_discount * (docs.amount_vat / 100)
        data['contact_person'] = docs.contact_person_txt

        data['amount_tax'] = docs.amount_tax
        data['amount_after_tax'] = formatLang(self.env, docs.amount_after_tax)

        # Supplier
        data['partner_vat_no'] = docs.partner_id.vat
        data['partner_bin_no'] = docs.partner_id.bin
        data['partner_tin_no'] = docs.partner_id.tin

        # Consignee
        data['company_vat_no'] = docs.company_id.partner_id.vat
        data['company_bin_no'] = docs.company_id.partner_id.bin
        data['company_tin_no'] = docs.company_id.partner_id.tin


        if docs.partner_id.child_ids:
            for con in docs.partner_id.child_ids[0]:
                if con.name and con.email and con.phone:
                    data['sup_con'] = con.name + ', ' + con.email + ', ' + con.phone
                elif con.name and con.email:
                    data['sup_con'] = con.name + ', ' + con.email
                elif con.name and con.phone:
                    data['sup_con'] = con.name + ', ' + con.phone
                elif con.email and con.phone:
                    data['sup_con'] = con.email + ', ' + con.phone
                else:
                    data['sup_con'] = con.name or con.email or con.phone
        else:
            data['sup_con']= ''

        if docs.order_line:
            for ol in docs.order_line:
                list_obj = {}
                list_obj['product_id']= ol.product_id.name
                list_obj['product_qty']= ol.product_qty
                unit_price = ol.price_subtotal / ol.product_qty
                list_obj['price_unit']= formatLang(self.env,unit_price)
                list_obj['product_uom'] = ol.product_uom.name
                list_obj['price_subtotal']= ol.price_subtotal
                list_obj['price_subtotal_price']= formatLang(self.env,ol.price_subtotal)
                total_amount.append(list_obj['price_subtotal'])
                order_list.append(list_obj)

        # sub total
        total = sum(total_amount)
        # grand total, here grand total field is docs.amount_total
        amt_to_word = self.env['res.currency'].amount_to_word(float(docs.amount_total), True, docs.currency_id.name)

        docargs = {
            'lists': order_list,
            'data': data,
            'total_amount': formatLang(self.env, total),
            'amt_to_word': amt_to_word,
            'order_date': order_date
        }

        return self.env['report'].render('gbs_purchase_order.report_purchase_order', docargs)