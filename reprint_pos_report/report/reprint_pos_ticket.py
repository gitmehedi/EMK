from openerp import api, models


class ReprintSalePosTicket(models.AbstractModel):
    _name = 'report.reprint_pos_report.reprint_sale_ticket'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('reprint_pos_report.reprint_sale_ticket')
        pos_order = self.env['pos.order'].search([('id', '=', self.id)])

        if pos_order:
            reprint = True if pos_order.pos_reference else False
            main_header = {
                'company_name': pos_order.company_id.name,
                'shop_name': pos_order.session_id.config_id.name,
                'street': pos_order.session_id.config_id.operating_unit_id.street,
                'street2': pos_order.session_id.config_id.operating_unit_id.street2,
                'city': pos_order.session_id.config_id.operating_unit_id.city,
                'zip': pos_order.session_id.config_id.operating_unit_id.zip,
                'vat': pos_order.session_id.config_id.operating_unit_id.vat,
                'contact_no': pos_order.session_id.config_id.operating_unit_id.contact_no,
            }
            sub_header = {
                'order_id': pos_order.pos_reference,
                'customer_name': pos_order.partner_id.name if pos_order.partner_id.name else 'Unknown',
                'cashier': pos_order.user_id.name,
                'date_order': pos_order.date_order,
                'receipt_header': pos_order.session_id.config_id.receipt_header,
                'receipt_footer': pos_order.session_id.config_id.receipt_footer,
            }
            total_discount = 0
            total_quantity = 0
            orderlines = []
            for line in pos_order.lines:
                rec = {}
                rec['product_name'] = line.product_id.name
                rec['discount'] = line.discount
                rec['quantity'] = "{0:.2f} {1}".format(line.qty,line.product_id.uom_id.name)
                rec['rate'] = int(line.price_unit)
                rec['vat'] = "{0:.2f}".format(line.price_subtotal_incl - line.price_subtotal)
                rec['total_amount'] = line.price_subtotal
                total_discount = total_discount + line.price_unit * line.qty - line.price_subtotal
                total_quantity = total_quantity + line.qty
                orderlines.append(rec)

            total_value = {
                'total': pos_order.amount_total - pos_order.amount_tax,
                'discount': total_discount,
                'quantity': int(total_quantity),
                'vat': pos_order.amount_tax,
                'net_amount': pos_order.amount_total
            }
            journal = []
            for record in pos_order.statement_ids:
                rec = {}
                rec['name'] = 'Change:' if record.amount < 0 else record.journal_id.display_name
                rec['amount'] = record.amount
                journal.append(rec)

        docargs = {
            'doc_ids': self._ids,
            'main_header': main_header,
            'sub_header': sub_header,
            'orderlines': orderlines,
            'total_value': total_value,
            'reprint': reprint,
            'payment': journal,
            'doc_model': report.model,
            'docs': self,
        }
        return report_obj.render('reprint_pos_report.reprint_sale_ticket', docargs)
