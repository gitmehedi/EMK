from odoo import api, exceptions, fields, models
from odoo.tools.misc import formatLang
from datetime import date, datetime


class CustomerInvoice(models.AbstractModel):
    _name = 'report.account_reports_extend.report_customer_invoice_document'

    @api.multi
    def render_html(self, docids, data=None):
        po_run_pool = self.env['account.invoice']
        if data.get('active_id'):
            docs = po_run_pool.browse(data.get('active_id'))
        else:
            docs = po_run_pool.browse(docids[0])
        report_utility_pool = self.env['report.utility']

        data = {}
        invoice_line_ids = []
        total_payable_amount = 0
        if docs.invoice_line_ids:
            for ol in docs.invoice_line_ids:
                list_obj = {}
                list_obj['product_name'] = ol.product_id.name
                list_obj['product_qty'] = ol.quantity
                list_obj['price_unit'] = formatLang(self.env, ol.price_unit)
                list_obj['product_uom'] = ol.uom_id.name
                list_obj['currency'] = ol.currency_id.name
                list_obj['price_subtotal'] = formatLang(self.env, ol.price_total)
                total_payable_amount += ol.price_total
                invoice_line_ids.append(list_obj)

        tax_line_ids = []
        tax_line_total = 0
        if docs.tax_line_ids:
            for tl in docs.tax_line_ids:
                list_obj = {}
                list_obj['narration'] = tl.name
                list_obj['gl_name'] = tl.account_id.name
                list_obj['amount'] = formatLang(self.env, tl.amount)
                tax_line_total += tl.amount
                tax_line_ids.append(list_obj)
        challan_no = ''
        date_done = False
        if docs.picking_ids:
            for picking_id in docs.picking_ids:
                challan_no = picking_id.name
                datetime_str = picking_id.date_done
                date_done = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S').date()

        contact_person = False
        contact_number = False
        for contact in docs.partner_id.child_ids:
            if contact.type == 'contact':
                contact_person = contact.name
                contact_number = contact.phone if contact.phone else contact.mobile

        data['number'] = docs.number
        data['origin'] = docs.origin
        data['current_date'] = report_utility_pool.get_date_from_string(str(date.today()))
        data['date_due'] = report_utility_pool.get_date_from_string(docs.date_due)
        data['date_done'] = report_utility_pool.get_date_from_string(str(date_done))
        data['challan_no'] = challan_no
        data['bin_number'] = docs.partner_id.bin
        data['contact_person'] = contact_person
        data['contact_number'] = contact_number
        data['partner_name'] = docs.partner_id.name
        data['partner_address'] = report_utility_pool.getCoustomerAddress(docs.partner_id)
        data['address'] = report_utility_pool.getBranchAddress(docs.company_id)

        data['comment'] = docs.comment


        docargs = {
            'invoice_line_ids': invoice_line_ids,
            'tax_line_ids': tax_line_ids,
            'data': data,
            'tax_line_total': formatLang(self.env, tax_line_total),
            'in_word_amount': self.env['res.currency'].amount_to_word(float(total_payable_amount)),
            'total_payable_amount': formatLang(self.env, total_payable_amount)
        }

        return self.env['report'].render('account_reports_extend.report_customer_invoice_document', docargs)