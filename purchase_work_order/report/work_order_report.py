from openerp import api, fields, models, _


class HrLeaveSummaryReport(models.AbstractModel):
    _name = 'report.purchase_work_order.report_product_work_order'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        data, header, attr, lists = {}, {}, {}, []
        purchase = self.env['purchase.order'].search([('id', 'in', self._ids)])

        for record in purchase.order_line:
            for rec in record.product_id.attribute_line_ids:
                attr[rec.display_name] = rec.display_name

        if purchase:
            data['name'] = purchase.name
            data['order_date'] = purchase.date_order
            data['partner_name'] = purchase.partner_id
            data['partner_ref'] = purchase.partner_ref
            data['amount_untaxed'] = purchase.amount_untaxed
            data['amount_tax'] = purchase.amount_tax
            data['amount_total'] = purchase.amount_total
            data['amount_to_word'] = float(purchase.amount_total)
            data['notes'] = purchase.notes

            header[0] = 'S.N'
            header[len(header)] = 'Name of Product'
            header[len(header)] = 'UoM'
            header[len(header)] = 'Order Qty'
            header[len(header)] = 'Production Terms'
            header[len(header)] = 'Delivery Date'
            header[len(header)] = 'Unit Price'
            header[len(header)] = 'Amount'
            header[len(header)] = 'Remarks'

        for list in purchase.order_line:
            prod = {}
            prod['name'] = list.product_id.display_name
            prod['uom'] = list.product_uom.name
            prod['qty'] = "{0:.2f}".format(list.product_qty)
            prod['production_terms'] = list.production_term_id.name
            prod['date_planned'] = list.date_planned
            prod['price_unit'] = list.price_unit
            prod['tax_amount'] = "Tax {0:.2f}%".format(list.taxes_id.amount)
            prod['price_total'] = list.price_subtotal
            prod['remarks'] = list.remarks

            lists.append(prod)

        docargs = {
            'data': data,
            'holiday_objs': lists,
            'header': header,
            'purchase': purchase
        }
        return report_obj.render('purchase_work_order.report_product_work_order', docargs)
