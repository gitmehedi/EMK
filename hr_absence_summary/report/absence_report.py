# -*- coding: utf-8 -*-
##############################################################################

import time
from openerp import api, exceptions, fields, models
from openerp.tools.translate import _

    
class ReportAbsenceLists(models.AbstractModel):
    _name = 'report.hr_absence_summary.report_absence_view_qweb'
    
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('hr_absence_summary.report_absence_view_qweb')

        holiday_lists = self.env['calendar.holiday.type'].search([('status', '=', True)])
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': holiday_lists,
            'form': data['form'],
            'other':data['other']
        }
        return report_obj.render('hr_absence_summary.report_absence_view_qweb', docargs)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
