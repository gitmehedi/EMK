from odoo import api,models,fields
from odoo.tools.misc import formatLang


class LoanReport(models.AbstractModel):
    _name = "report.hr_employee_loan.report_hr_employee_loan"

    @api.multi
    def render_html(self,docids,data=None):
        loan_obj = self.env['hr.employee.loan'].browse(docids[0])

        data = {}
        data['loan_name'] = loan_obj.name
        data['employee_name'] = loan_obj.employee_id.name
        data['department_name'] = loan_obj.department_id.name
        data['loan_type'] = loan_obj.loan_type_id.name
        data['principal_amount'] = formatLang(self.env,loan_obj.principal_amount)
        data['interst_mode'] = loan_obj.interst_mode_id
        data['rate'] = loan_obj.req_rate
        data['applied_date'] = loan_obj.applied_date
        data['approved_date'] = loan_obj.approved_date
        data['disbursement_date'] = loan_obj.disbursement_date
        data['repayment_date'] = loan_obj.repayment_date
        data['amount_receive'] = formatLang(self.env,(loan_obj.principal_amount)-(loan_obj.remaining_loan_amount))
        data['amount_due'] = formatLang(self.env,loan_obj.remaining_loan_amount)

        installment_list= []
        policies_list = []
        if loan_obj.line_ids:
            for line in loan_obj.line_ids:
                list_obj = {}
                list_obj['num_installment'] = line.num_installment
                list_obj['schedule_date'] = line.schedule_date
                list_obj['installment'] = formatLang(self.env,line.installment)
                list_obj['state'] = line.state
                installment_list.append(list_obj)

        if loan_obj.employee_loan_policy_ids:
            for policy in loan_obj.employee_loan_policy_ids:
                policy_obj = {}
                policy_obj['name'] = policy.name
                policy_obj['code'] = policy.code
                policy_obj['type'] = policy.policy_type_id
                policy_obj['value'] = policy.value
                policies_list.append(policy_obj)

        docargs = {
            'data': data,
            'lists': installment_list,
            'policies_list': policies_list,
            'policys': loan_obj.employee_loan_policy_ids

        }
        return self.env['report'].render('hr_employee_loan.report_hr_employee_loan',docargs)