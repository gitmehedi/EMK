from odoo import api,models,fields

class PurchaseReport(models.AbstractModel):
    _name = "report.purchase_reports.report_pending_purchase"

    @api.multi
    def render_html(self,docids,data=None):
        # purchase_obj = self.env['hr.employee.loan']
        record_list = []
        if data['purchase_name'] == 'Pending Local Purchase Report':

            # for rec in purchase_obj:
            #     if rec.line_ids:
            #         for line in purchase_obj.line_ids:
            list_obj = {}
            list_obj['pr_no'] = 'PR-SCCL-DF-2018-000056'
            list_obj['items'] = 'Motor Cooling fan-5'
            list_obj['qty'] = '24'
            list_obj['unit'] = 'Pcs'
            list_obj['last_rate'] = '120'
            list_obj['po_no'] = 'PO-SCCL-DF-2018-000049'
            list_obj['po_qty'] = '33'
            list_obj['mrr_qty'] = '20'
            list_obj['remaining_qty'] = '7'
            record_list.append(list_obj)
        else:
            # for rec in purchase_obj:
            #     if rec.line_ids:
            #         for line in purchase_obj.line_ids:
            list_obj = {}
            list_obj['pr_no'] = 'PR-SCCL-DF-2018-000056'
            list_obj['items'] = 'Motor Cooling fan-5'
            list_obj['qty'] = '24'
            list_obj['unit'] = 'Pcs'
            list_obj['last_rate'] = '120'
            list_obj['po_no'] = 'PO-SCCL-DF-2018-000049'
            list_obj['po_qty'] = '33'
            list_obj['mrr_qty'] = '20'
            list_obj['remaining_qty'] = '7'
            record_list.append(list_obj)

        docargs = {
            'data': data,
            'name':data['purchase_name'],
            'lists': record_list,

        }
        return self.env['report'].render('purchase_reports.report_pending_purchase', docargs)