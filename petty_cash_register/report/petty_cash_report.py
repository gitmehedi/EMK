# -*- coding: utf-8 -*-
##############################################################################
import time
from openerp import api, exceptions, fields, models
from openerp.tools.translate import _

    
class ReportPettyCashQweb(models.AbstractModel):
    _name = 'report.petty_cash_register.report_petty_cash_qweb'
    
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('petty_cash_register.report_petty_cash_qweb')
        print '_-------------------------+',self
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': data['ids'],
            'form': data['form1'],
        }
        return report_obj.render('petty_cash_register.report_petty_cash_qweb', docargs)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
