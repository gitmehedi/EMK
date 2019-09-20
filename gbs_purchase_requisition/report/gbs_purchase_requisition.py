from odoo import api, exceptions, fields, models
from odoo.tools.misc import formatLang


class GbsPurchaseRequisition(models.AbstractModel):
    _name = 'report.gbs_purchase_requisition.report_purchase_requisition'

    @api.multi
    def render_html(self, docids, data=None):
        pr_pool = self.env['purchase.requisition']
        pr_obj = pr_pool.browse(docids[0])
        report_utility_pool = self.env['report.utility']
        order_list = []

        data = {}
        data['name'] = pr_obj.name
        data['requisition_date'] = pr_obj.requisition_date
        requisition_date = report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(data['requisition_date']))
        data['department_id'] = pr_obj.dept_location_id.name or False
        #@Todo Need to get Location ID
        data['address'] = report_utility_pool.getAddressByUnit(pr_obj.operating_unit_id)
        if pr_obj.line_ids:
            for line in pr_obj.line_ids:
                list_obj = {}
                list_obj['product_id']= line.product_id.name
                list_obj['store_code']= line.store_code
                list_obj['product_ordered_qty']= line.product_ordered_qty
                list_obj['product_uom_id']= line.product_uom_id.name
                list_obj['total']= formatLang(self.env, line.product_ordered_qty*line.price_unit)
                list_obj['last_purchase_date']= line.last_purchase_date
                list_obj['last_qty']= line.last_qty
                list_obj['last_price_unit']= formatLang(self.env, line.last_price_unit)
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