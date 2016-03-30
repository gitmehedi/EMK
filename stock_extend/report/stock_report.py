# -*- coding: utf-8 -*-
##############################################################################

import time
from openerp import api, exceptions, fields, models
from openerp.tools.translate import _
#from openerp.report import report_sxw

"""
class StockReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(StockReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'get_start_date': self._get_start_date,
            'get_end_date': self._get_end_date,
        })
        
    def _get_start_date(self, data):
        if data.get('form', False) and data['form'].get('start_date', False):
            return data['form']['start_date']
        return ''
    
    def _get_end_date(self, data):
        if data.get('form', False) and data['form'].get('end_date', False):
            return data['form']['end_date']
        return ''
    
    def set_context(self, objects, data, ids, report_type=None):
        print '------------ data---------', data
        ctx2 = data['form'].get('used_context',{}).copy()
        
        return super(StockReport, self).set_context(objects, data, [], report_type)
    
    def lines(self, data):
         return data
    
# class ReportStockQweb(models.AbstractModel):
#    _name = 'report.stock_extend.report_stock_issue_qweb'
#    _inherit = 'report.abstract_report'
#    _template = 'stock_extend.report_stock_issue_qweb'
#    _wrapped_report_class = StockReport
    """
    
class ReportStockQweb(models.AbstractModel):
    _name = 'report.stock_extend.report_stock_issue_qweb'
    
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('stock_extend.report_stock_issue_qweb')
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': data['ids'],
            'form': data['form'],
            'other':data['other']
        }
        print '+++++++++=== docargs -----',docargs
        return report_obj.render('stock_extend.report_stock_issue_qweb', docargs)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
