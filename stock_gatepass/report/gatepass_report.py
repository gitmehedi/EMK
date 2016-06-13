# -*- coding: utf-8 -*-
##############################################################################

import time
from openerp import api, exceptions, fields, models
from openerp.tools.translate import _
from datetime import datetime

class ReportGatePassQweb(models.AbstractModel):
    _name = 'report.stock_gatepass.report_gate_pass_qweb'
    
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('stock_gatepass.report_gate_pass_qweb')
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': data['ids'],
            'form': data['form'],
            'other':data['other'],
        }
        
        return report_obj.render('stock_gatepass.report_gate_pass_qweb', docargs)



