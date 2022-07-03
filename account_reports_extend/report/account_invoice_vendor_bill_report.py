from odoo import api, exceptions, fields, models
from odoo.tools.misc import formatLang


class AccountInvoiceVendorBill(models.AbstractModel):
    _name = 'report.account_reports_extend.report_vendor_bill_document'

    def _get_checked_by_name_designation(self, res_id, name):
        e_name = designation = ''
        if name:
            query = """
            select write_uid from mail_message
            where res_id=%s and model='account.invoice' and TRIM(record_name)='%s' LIMIT 1
            """ % (res_id, name)
            self._cr.execute(query)
            fetched_data = self._cr.dictfetchall()[0]
            checked_by_id = fetched_data['write_uid']
            hr_employee = self.env['hr.employee'].search([('user_id', '=', checked_by_id)])
            e_name = hr_employee.name
            designation = hr_employee.job_id.name
        return e_name, designation

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

        data['number'] = docs.number
        data['origin'] = docs.origin
        # data['date_invoice'] = report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(docs.date_invoice))
        data['date_invoice'] = report_utility_pool.get_date_from_string(docs.date_invoice)
        data['reference'] = docs.reference
        data['partner_name'] = docs.partner_id.name
        data['partner_address'] = report_utility_pool.getCoustomerAddress(docs.partner_id)
        data['company_name'] = docs.company_id.name
        data['operating_unit'] = docs.operating_unit_id.name
        data['company_name'] = docs.company_id.name
        data['tax_and_other_adjustment'] = formatLang(self.env, tax_line_total)
        net_payable = total_payable_amount - tax_line_total
        data['net_payable'] = formatLang(self.env, net_payable)

        payment_amount = advance_amount = 0
        payment_move_line_ids = docs.payment_move_line_ids
        for payment in payment_move_line_ids:
            if docs.type in ('out_invoice', 'in_refund'):
                pass
                # amount = sum([p.amount for p in payment.matched_debit_ids if p.debit_move_id in docs.move_id.line_ids])
                # amount_currency = sum(
                #     [p.amount_currency for p in payment.matched_debit_ids if p.debit_move_id in docs.move_id.line_ids])

            elif docs.type in ('in_invoice', 'out_refund'):
                display_name = payment.display_name[0:2]
                if display_name == 'VA':
                    amount = sum([p.amount for p in payment.matched_credit_ids if p.credit_move_id in docs.move_id.line_ids])

                    advance_amount += amount
                else:
                    amount = sum(
                        [p.amount for p in payment.matched_credit_ids if p.credit_move_id in docs.move_id.line_ids])
                    payment_amount += amount

        data['total_advance_adjustment'] = formatLang(self.env, advance_amount)
        data['total_amount_due_outstanding'] = formatLang(self.env, net_payable-advance_amount)
        data['payment'] = formatLang(self.env, payment_amount)
        data['net_amount_due_outstanding'] = formatLang(self.env, docs.residual)
        data['prepare_by'] = docs.create_uid.name
        hr_employee = self.env['hr.employee'].search([('user_id', '=', docs.create_uid.id)])
        data['prepare_by_designation'] = ""
        if hr_employee:
            data['prepare_by_designation'] = hr_employee.job_id.name

        checked_by_name_designation = self._get_checked_by_name_designation(docs.id, docs.number)
        data['checked_by'] = checked_by_name_designation[0]
        data['checked_by_designation'] = checked_by_name_designation[1]
        data['verified_by'] = ""
        data['verified_by_designation'] = ""
        data['comment'] = docs.comment


        docargs = {
            'invoice_line_ids': invoice_line_ids,
            'tax_line_ids': tax_line_ids,
            'data': data,
            'tax_line_total': formatLang(self.env, tax_line_total),
            'total_payable_amount': formatLang(self.env, total_payable_amount)
        }

        return self.env['report'].render('account_reports_extend.report_vendor_bill_document', docargs)