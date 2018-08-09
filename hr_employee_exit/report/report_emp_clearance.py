from odoo import api,models,fields

class LoanReport(models.AbstractModel):
    _name = "report.hr_employee_exit.report_employee_clearance"

    @api.multi
    def render_html(self, docids, data=None):
        exit_obj = self.env['hr.emp.exit.req'].browse(docids[0])

        data={}
        data['employee_id'] = exit_obj.employee_id.name
        data['req_date'] = exit_obj.req_date
        data['last_date'] = exit_obj.last_date
        data['initial_employment_date'] = exit_obj.employee_id.initial_employment_date
        data['department_id'] = exit_obj.department_id.name
        data['job_id'] = exit_obj.job_id.name
        data['emp_code'] = exit_obj.employee_id.device_employee_acc


        checklist=[]
        if exit_obj.checklists_ids:
            for line in exit_obj.checklists_ids:
                dept_list=[]
                dept= line.responsible_department
                dept_list.append(dept)
                for dept in dept_list:
                    if dept == line.responsible_department:
                        list_obj={}
                        list_obj['responsible_department'] = line.responsible_department.name
                        list_obj['user'] = {}
                        list_obj['user']['checklist_item'] = line.checklist_item_id.name
                        list_obj['user']['remarks']  = line.remarks
                        list_obj['user']['state']  = line.state

                checklist.append(list_obj)

        docargs = {
            'data': data,
            'lists': checklist
        }

        return self.env['report'].render('hr_employee_exit.report_employee_clearance',docargs)