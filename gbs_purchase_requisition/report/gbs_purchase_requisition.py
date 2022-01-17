from odoo import api, exceptions, fields, models
from odoo.tools.misc import formatLang


class GbsPurchaseRequisition(models.AbstractModel):
    _name = 'report.gbs_purchase_requisition.report_purchase_requisition'

    @api.multi
    def render_html(self, docids, data=None):
        pr_pool = self.env['purchase.requisition']
        pr_obj = pr_pool.browse(docids[0])
        report_utility_pool = self.env['report.utility']
        ReportUtility = self.env['report.utility']
        order_list = []
        indent_list = []
        data = {}
        data['name'] = pr_obj.name
        data['requisition_date'] = pr_obj.requisition_date
        requisition_date = report_utility_pool.getERPDateFormat(
            report_utility_pool.getDateFromStr(data['requisition_date']))
        data['department_id'] = pr_obj.dept_location_id.name or False
        # @Todo Need to get Location ID
        data['address'] = report_utility_pool.getAddressByUnit(pr_obj.operating_unit_id)
        if pr_obj.line_ids:
            for line in pr_obj.line_ids:
                list_obj = {}
                list_obj['product_id'] = line.product_id.name
                list_obj['store_code'] = line.store_code
                list_obj['product_ordered_qty'] = line.product_ordered_qty
                list_obj['product_uom_id'] = line.product_uom_id.name
                list_obj['total'] = formatLang(self.env, line.product_ordered_qty * line.price_unit)
                list_obj['last_purchase_date'] = line.last_purchase_date
                list_obj['last_qty'] = line.last_qty
                list_obj['last_price_unit'] = formatLang(self.env, line.last_price_unit)
                list_obj['product_qty'] = line.product_qty
                list_obj['remark'] = line.remark
                order_list.append(list_obj)

        if pr_obj.indent_ids:
            for indent in pr_obj.indent_ids:
                ind_list_obj = {}
                ind_list_obj['indent_name'] = indent.name
                indent_list.append(ind_list_obj)
        else:
            indent_list = []

        # PR Report Employee approval sign Automation Query
        _pr_log_sql = """
            SELECT code,employee_name,action_name,performer_id,emp_department_name, max(perform_date) as perform_date FROM 
                (SELECT ua.code as code,ua.name as action_name,pral.performer_id as performer_id,
                rp.name as employee_name, hd.name as emp_department_name,
                (pral.perform_date + interval '6h') as perform_date  FROM purchase_requisition_action_log pral
                LEFT JOIN users_action ua ON ua.id=pral.action_id
                LEFT JOIN res_users ru on pral.performer_id = ru.id
                LEFT JOIN res_partner rp on ru.partner_id = rp.id
                LEFT JOIN resource_resource rr ON rr.user_id = ru.id
                LEFT JOIN hr_employee emp ON emp.resource_id = rr.id
                LEFT JOIN hr_department hd ON emp.department_id = hd.id
                WHERE requisition_id = %s) t1 
                GROUP BY code,employee_name,action_name,performer_id,emp_department_name

        """ % pr_obj.id

        self.env.cr.execute(_pr_log_sql)

        pr_confirm_by = ''
        pr_confirmation_time = ''
        pr_confirmation_dept = ''
        pr_approved_by = ''
        pr_approval_time = ''
        pr_approval_dept = ''
        pr_validated_by = ''
        pr_validation_time = ''
        pr_validation_dept = ''
        previous_code = ''
        for vals in self.env.cr.dictfetchall():
            if previous_code == vals['code']:
                continue
            if vals['code'] == 1:
                # PR CONFIRM
                pr_confirm_by = vals['employee_name']
                pr_confirmation_time = str(vals['perform_date'])
                pr_confirmation_dept = vals['emp_department_name']
            elif vals['code'] == 2:
                # PR VALIDATE
                pr_validated_by = vals['employee_name']
                pr_validation_time = str(vals['perform_date'])
                pr_validation_dept = vals['emp_department_name']
            elif vals['code'] == 3:
                # PR APPROVE
                pr_approved_by = vals['employee_name']
                pr_approval_time = str(vals['perform_date'])
                pr_approval_dept = vals['emp_department_name']
            previous_code = vals['code']

        docargs = {
            'lists': order_list,
            'data': data,
            'requisition_date': requisition_date,
            'address': data['address'],
            'indent_list': indent_list,
            'pr_confirm_by': pr_confirm_by,
            'pr_confirmation_time': ReportUtility.get_date_time_from_string(pr_confirmation_time),
            'pr_confirmation_dept': pr_confirmation_dept,
            'pr_approved_by': pr_approved_by,
            'pr_approval_time': ReportUtility.get_date_time_from_string(pr_approval_time),
            'pr_approval_dept': pr_approval_dept,
            'pr_validated_by': pr_validated_by,
            'pr_validation_time': ReportUtility.get_date_time_from_string(pr_validation_time),
            'pr_validation_dept': pr_validation_dept

        }

        return self.env['report'].render('gbs_purchase_requisition.report_purchase_requisition', docargs)
