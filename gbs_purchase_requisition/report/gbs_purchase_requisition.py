from odoo import api, exceptions, fields, models

class GbsPurchaseRequisition(models.AbstractModel):
    _name = 'report.gbs_purchase_requisition.report_purchase_requisition'

    @api.multi
    def render_html(self, docids, data=None):
        po_run_pool = self.env['purchase.requisition']
        docs = po_run_pool.browse(docids[0])
        report_utility_pool = self.env['report.utility']
        order_list = []
        address = []
        if docs.operating_unit_id.partner_id.street:
            address.append(docs.operating_unit_id.partner_id.street)

        if docs.operating_unit_id.partner_id.street2:
            address.append(docs.operating_unit_id.partner_id.street2)

        if docs.operating_unit_id.partner_id.zip_id:
            address.append(docs.operating_unit_id.partner_id.zip_id.name)

        if docs.operating_unit_id.partner_id.city:
            address.append(docs.operating_unit_id.partner_id.city)

        if docs.operating_unit_id.partner_id.state_id:
            address.append(docs.operating_unit_id.partner_id.state_id.name)

        if docs.operating_unit_id.partner_id.country_id:
            address.append(docs.operating_unit_id.partner_id.country_id.name)

        str_address = ', '.join(address)

        data = {}
        data['name'] = docs.name
        data['requisition_date'] = docs.requisition_date
        requisition_date = report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(data['requisition_date']))
        data['department_id'] = docs.department_id.name
        data['address'] = str_address
        if docs.line_ids:
            for line in docs.line_ids:
                list_obj = {}
                list_obj['product_id']= line.product_id.name
                list_obj['store_code']= line.store_code
                list_obj['product_ordered_qty']= line.product_ordered_qty
                list_obj['product_uom_id']= line.product_uom_id.name
                list_obj['total']= line.product_ordered_qty*line.price_unit
                list_obj['last_purchase_date']= line.last_purchase_date
                list_obj['last_qty']= line.last_qty
                list_obj['last_price_unit']= line.last_price_unit
                list_obj['product_qty']= line.product_qty
                list_obj['remark']= line.remark
                order_list.append(list_obj)

        docargs = {
            'lists': order_list,
            'data': data,
            'requisition_date': requisition_date,
            'address': data['address'],
        }

        return self.env['report'].render('gbs_purchase_requisition.report_purchase_requisition', docargs)