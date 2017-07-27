# -*- coding: utf-8 -*-
##############################################################################
from openerp import api, models
from datetime import datetime


class DailyCreditSettlementReport(models.AbstractModel):
    _name = 'report.pos_summary_report.report_pos_summary_qweb'

    def _generate_categories(self, category, categories):
        categories.append(category.id)
        for cat in category.child_id:
            categories = self._generate_categories(cat, categories)
        return categories

    def _generate_lines(self, start_date, end_date, pos_config):

        query = """
                SELECT * FROM pos_order po 
                    INNER JOIN stock_location sl
                    ON (po.location_id = sl.id )
                    INNER JOIN pos_config pc
                    ON (pc.stock_location_id = sl.id )
                    WHERE pc.id = %s and date_order between %s and %s 
                    ORDER BY po.date_order;
        """
        params = (pos_config, start_date, end_date)
        self.env.cr.execute(query, params)
        res = self.env.cr.dictfetchall()
        return res

    @api.multi
    def render_html(self, data=None):
        lines = []
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('stock_summary_report.report_stock_summary_qweb')
        # cash_counter = self.env['pos.config'].search([('stock_location_id', '=', data['location_id'])])

        domain = []
        if data['point_of_sale_id']:
            domain.append(('point_of_sale_id', '=', data['point_of_sale_id']))
        if data['start_date']:
            domain.append(('date_order', '>=', data['start_date']))
        if data['end_date']:
            domain.append(('date_order', '<=', data['end_date']))

        order_list = self.env['pos.order'].search(domain, order="date_order asc")


        for record in order_list:
            rec = {}
            sales_value = sum([r.qty * r.price_unit for r in record.lines])
            discount = sum([r.qty * r.price_unit - r.price_subtotal for r in record.lines])
            rec['date_order'] = self.format_date(record.date_order)
            rec['pos_reference'] = record.pos_reference
            rec['sales_value'] = self.decimal(sales_value)
            rec['amount_tax'] = self.decimal(record.amount_tax)
            rec['discount'] = 0 if discount == 0 else '- {0}'.format(self.decimal(discount))
            rec['net_sales'] = self.decimal(record.amount_total)
            cash, card = 0, 0

            for statement in record.statement_ids:
                if statement.journal_id.name == 'Cash':
                    cash = cash + statement.amount
                if statement.journal_id.name == 'Card':
                    card = card + statement.amount

            rec['cash'] = self.decimal(cash)
            rec['credit_card'] = self.decimal(card)
            rec['total'] = self.decimal(cash + card)
            lines.append(rec)

        address = {
            'name': self.env.user.company_id.name,
            'contact1': self.env.user.default_operating_unit_id.partner_id.street,
            'contact2': self.env.user.default_operating_unit_id.partner_id.street,
            'phone': self.env.user.default_operating_unit_id.partner_id.phone
        }
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'start_date': data['start_date'],
            'end_date': data['end_date'],
            'category_id': data['point_of_sale_id'],
            'lines': lines,
            'address': address,
            'pos_config': 'name'
        }
        return report_obj.render('pos_summary_report.report_pos_summary_qweb', docargs)

    def format_date(self, date):
        return datetime.strptime(date[:10], '%Y-%m-%d').strftime('%d-%m-%Y')

    def decimal(self, val):
        return "{0:.2f}".format(round(val, 2))
