from odoo import api,models,fields

class ExitReport(models.AbstractModel):
    _name = "report.hr_employee_exit.report_employee_exit"

    @api.multi
    def render_html(self, docids, data=None):
        exit_obj = self.env['hr.emp.exit.req'].browse(docids[0])

        data={}
        data['employee_id'] = exit_obj.employee_id.name
        data['req_date'] = exit_obj.req_date
        data['last_date'] = exit_obj.last_date
        data['manager_id'] = exit_obj.manager_id.name
        data['department_id'] = exit_obj.department_id.name
        data['job_id'] = exit_obj.job_id.name
        data['confirm_by'] = exit_obj.confirm_by.name
        data['approver1_by'] = exit_obj.approver1_by.name
        data['approver2_by'] = exit_obj.approver2_by.name
        data['confirm_date'] = exit_obj.confirm_date
        data['approved1_date'] = exit_obj.approved1_date
        data['approved2_date'] = exit_obj.approved2_date
        data['emp_notes'] = exit_obj.emp_notes
        data['reason_for_exit'] = exit_obj.reason_for_exit

        checklist=[]
        if exit_obj.checklists_ids:
            for line in exit_obj.checklists_ids:
                list_obj={}
                list_obj['checklist_item']  = line.checklist_item_id.name
                list_obj['responsible_employee']  = line.responsible_emp.name
                list_obj['responsible_department']  = line.responsible_department.name
                list_obj['remarks']  = line.remarks
                list_obj['state']  = line.state

                checklist.append(list_obj)

        docargs = {
            'data': data,
            'lists': checklist
        }
        return self.env['report'].render('hr_employee_exit.report_employee_exit', docargs)
