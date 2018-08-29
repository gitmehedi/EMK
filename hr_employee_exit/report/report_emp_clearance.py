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

        sql_dept = '''SELECT p.state as state,
                        item.name as item_name,
                        p.remarks as remarks,
                        dept.name as responsible_dept
                FROM 
                    hr_exit_checklists_line as p 
                left join 
                    hr_exit_checklist_item as item 
                on item.id = p.checklist_item_id
                left join 
                    hr_department as dept 
                on dept.id = p.responsible_department'''
        self.env.cr.execute(sql_dept)
        data_list = self.env.cr.dictfetchall()
        item_checklist = {vals['responsible_dept']: {'item_list': [], }
                    for vals in data_list}
        for vals in data_list:
            if vals:
                item_checklist[vals['responsible_dept']]['item_list'].append(vals)

        sql_emp = '''SELECT p.state AS state,
                        item.name AS item_name,
                        p.remarks AS remarks,
                        emp.name_related as responsible_emp
                    FROM
                        hr_exit_checklists_line AS p
                    LEFT JOIN
                        hr_exit_checklist_item as item
                    ON item.id = p.checklist_item_id
                    LEFT JOIN
                        hr_employee as emp
                    ON emp.id = p.responsible_emp'''
        self.env.cr.execute(sql_emp)
        data_list = self.env.cr.dictfetchall()
        checklist = {vals['responsible_emp']:{'item':[],}for vals in data_list}
        for vals in data_list:
            if vals:
                checklist[vals['responsible_emp']]['item'].append(vals)


        docargs = {
            'data': data,
            'lists': item_checklist,
            'checklist': checklist
        }

        return self.env['report'].render('hr_employee_exit.report_employee_clearance',docargs)