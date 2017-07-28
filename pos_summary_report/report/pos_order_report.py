from datetime import datetime

from openerp import api, models


class DailyCreditSettlementReport(models.AbstractModel):
    _name = 'report.pos_summary_report.report_pos_summary_qweb'

    @api.multi
    def render_html(self, data=None):
        lines = []
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('stock_summary_report.report_stock_summary_qweb')

        domain = []
        if data['operating_unit_id']:
            domain.append(('operating_unit_id', '=', data['operating_unit_id']))
        if data['point_of_sale_id']:
            domain.append(('point_of_sale_id', '=', data['point_of_sale_id']))
        if data['start_date']:
            domain.append(('date_order', '>=', data['start_date']))
        if data['end_date']:
            domain.append(('date_order', '<=', data['end_date']))

        order_list = self.env['pos.order'].search(domain, order="date_order asc")

        grand_total = {
            'sales_value': 0,
            'amount_tax': 0,
            'discount': 0,
            'net_sales': 0,
            'cash': 0,
            'card': 0,
            'total': 0,
        }

        for record in order_list:
            rec = {}
            sales_value = sum([r.qty * r.price_unit for r in record.lines])
            discount = sum([r.qty * r.price_unit - r.price_subtotal for r in record.lines])
            rec['date_order'] = self.format_date(record.date_order)
            rec['pos_reference'] = record.pos_reference
            rec['sales_value'] = self.decimal(sales_value)
            rec['amount_tax'] = self.decimal(record.amount_tax)
            rec['discount'] = '' if discount == 0 else '- {0}'.format(
                self.decimal(discount)) if discount > 0 else discount
            rec['net_sales'] = self.decimal(record.amount_total)
            cash, card = 0, 0

            for statement in record.statement_ids:
                if statement.journal_id.name == 'Cash':
                    cash = cash + statement.amount
                if statement.journal_id.name == 'Card':
                    card = card + statement.amount

            rec['cash'] = self.decimal(cash) if cash else ''
            rec['credit_card'] = self.decimal(card) if card else ''
            rec['total'] = self.decimal(cash + card)

            grand_total['sales_value'] = grand_total['sales_value'] + sales_value
            grand_total['amount_tax'] = grand_total['amount_tax'] + record.amount_tax
            grand_total['discount'] = grand_total['discount'] + discount
            grand_total['net_sales'] = grand_total['net_sales'] + record.amount_total
            grand_total['cash'] = grand_total['cash'] + cash
            grand_total['card'] = grand_total['card'] + card
            grand_total['total'] = grand_total['total'] + cash + card

            lines.append(rec)

        header = self.env['operating.unit'].search([('id', '=', data['operating_unit_id'])])

        total = {
            'sales_value': self.decimal(grand_total['sales_value']),
            'amount_tax': self.decimal(grand_total['amount_tax']),
            'discount': '' if grand_total['discount'] == 0 else '- {0}'.format(self.decimal(grand_total['discount'])) if
            grand_total['discount'] > 0 else self.decimal(grand_total['discount']),
            'net_sales': self.decimal(grand_total['net_sales']),
            'cash': self.decimal(grand_total['cash']),
            'card': self.decimal(grand_total['card']),
            'total': self.decimal(grand_total['total']),
        }

        address = {
            'name': header.name,
            'street': header.street,
            'street2': header.street2,
            'city': header.city,
            'zip': header.zip,
            'contact_no': header.contact_no
        }
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'data': data,
            'end_date': data['end_date'],
            'category_id': data['point_of_sale_id'],
            'lines': lines,
            'address': address,
            'pos_config': 'name',
            'total': total
        }
        return report_obj.render('pos_summary_report.report_pos_summary_qweb', docargs)

    def format_date(self, date):
        return datetime.strptime(date[:10], '%Y-%m-%d').strftime('%d-%m-%Y')

    def decimal(self, val):
        return "{:,}".format(round(val, 0))
