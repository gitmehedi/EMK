from openerp import api, fields, models
import math

class HrAttendanceSummaryReport(models.AbstractModel):
    _name = 'report.hr_attendance_and_ot_summary.report_att_summary'
    
    @api.model
    def render_html(self, docids, data=None):
        payslip_run_pool = self.env['hr.attendance.summary']
        docs = payslip_run_pool.browse(docids[0])

        dept = self.env['hr.department'].search([])
        dpt_att_summary_list = []
        sn = 1
        
        for d in dept:
            dpt_att_summary = {}
            dpt_att_summary['name'] = d.name
            dpt_att_summary['seq'] = d.sequence
            dpt_att_summary['val'] = []
            
            for att_sum in docs.att_summary_lines:
                if d.id == att_sum.employee_id.department_id.id:
                    att_summary = {}
                    att_summary['emp_name'] = att_sum.employee_id.name
                    att_summary['designation'] = att_sum.employee_id.job_id.name
                    att_summary['emp_seq'] = att_sum.employee_id.employee_sequence
                    att_summary['salary_days'] = att_sum.salary_days
                    att_summary['present_days'] = att_sum.present_days
                    att_summary['absent_days_count'] = att_sum.absent_days_count
                    att_summary['late_days_count'] = att_sum.late_days_count
                    att_summary['leave_days'] = att_sum.leave_days
                    att_summary['weekend_days_count'] = att_sum.weekend_days_count
                    att_summary['holidays_days'] = att_sum.holidays_days
                    att_summary['deduction_days'] = att_sum.deduction_days
                    att_summary['absent_deduction_days'] = att_sum.absent_deduction_days
                    # att_summary['late_hrs'] = att_sum.late_hrs
                    # att_summary['schedule_ot_hrs'] = att_sum.schedule_ot_hrs
                    # att_summary['cal_ot_hrs'] = att_sum.cal_ot_hrs
                    att_summary['late_hrs'] = self.convertFloatToTime(att_sum.late_hrs)
                    att_summary['schedule_ot_hrs'] = self.convertFloatToTime(att_sum.schedule_ot_hrs)
                    att_summary['cal_ot_hrs'] = self.convertFloatToTime(att_sum.cal_ot_hrs)

                    dpt_att_summary['val'].append(att_summary)
                    
            emp_sort_list  = dpt_att_summary['val']
            emp_sort_list = sorted(emp_sort_list, key=lambda k: k['emp_seq'])
            
            for ps in emp_sort_list:
                ps['sn'] = sn
                sn += 1
            
            dpt_att_summary['val'] = emp_sort_list
            dpt_att_summary_list.append(dpt_att_summary)

        pool_period = self.env['date.range'].search([('name','=',docs.period.name)])

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'hr.attendance.summary',
            'docs': dpt_att_summary_list,
            'doc_name': docs.name,
            'period_from': pool_period.date_start,
            'period_to': pool_period.date_end,
            'docs_len': 20,
            'state': docs.state,
        }

        return self.env['report'].render('hr_attendance_and_ot_summary.report_att_summary', docargs)

    ####################################################
    # Utility methods
    ####################################################

    def convertFloatToTime(self, float_value):
        return "%02d:%02d" % (float_value,math.modf(float_value)[0]*60)
    