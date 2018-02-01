from openerp import api, fields, models, _


class HrLeaveSummaryReport(models.AbstractModel):
    _name = 'report.work_order_report.report_product_work_order'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        data, header, attr, lists = {}, {}, {}, []
        purchase = self.env['purchase.order'].search([('id', 'in', self._ids)])

        for record in purchase.order_line:
            for rec in record.product_id.product_tmpl_id.attribute_line_ids:
                attr[rec.display_name] = rec.display_name

        if purchase:
            data['name'] = purchase.name
            data['order_date'] = purchase.date_order
            data['partner_name'] = purchase.partner_id
            data['partner_ref'] = purchase.partner_ref
            data['amount_untaxed'] = purchase.amount_untaxed
            data['amount_tax'] = purchase.amount_tax
            data['amount_total'] = purchase.amount_total
            data['amount_to_word'] = self.env['res.currency'].amount_to_word(float(purchase.amount_total))
            data['notes'] = purchase.notes

            header[0] = 'S.N'
            header[1] = 'Name'
            for val in attr:
                header[len(header)] = val
            header[len(header)] = 'UoM'
            header[len(header)] = 'Qty'
            header[len(header)] = 'Unit Price'
            header[len(header)] = 'Taxes'
            header[len(header)] = 'Sub Total'

        for list in purchase.order_line:
            prod = {}
            prod['name'] = list.product_id.name
            prod['uom'] = list.product_uom.name
            prod['value'] = {val: None for val in attr}
            for val in list.product_id.attribute_value_ids:
                prod['value'][val.attribute_id.name] = val.name
            prod['qty'] = "{0:.2f}".format(list.product_qty)
            prod['price_unit'] = list.price_unit
            prod['tax_amount'] = "Tax {0:.2f}%".format(list.taxes_id.amount)
            prod['price_total'] = list.price_subtotal

            lists.append(prod)

        docargs = {
            'data': data,
            'holiday_objs': lists,
            'header': header,
            'purchase': purchase
        }
        return report_obj.render('work_order_report.report_product_work_order', docargs)
