# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp import tools


class ProductUsageHistoryAnalysis(osv.osv):
    _name = "product.usage.history.analysis.report"
    _description = "Product Usage History Analysis Report"
    _auto = False
    _order = 'period_id ASC, category_id desc'

    # value = fields.Float(string='Value', required=True)
    # product_id = fields.Many2one('product.product', string='Product')
    # period_id = fields.Many2one('account.period', string='Period',
    #                             domain="[('special','=',False),('state','=','draft')]")
    # uom_id = fields.Many2one(related='product_id.uom_id', string='Unit of Measurement')
    # category_id = fields.Many2one("", string='Product Category', readonly=True)
    # operating_unit_id = fields.Many2one('operating.unit', string='Branch', required=True,
    #                                     )
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        'uom_id': fields.many2one('product.uom', 'Reference Unit of Measure', required=True),
        'value': fields.integer('Total', readonly=True),  # TDE FIXME master: rename into unit_quantity
        'category_id': fields.many2one('product.category', 'Category', readonly=True),
        'operating_unit_id': fields.many2one('operating.unit', 'Operating Unit', readonly=True),
        'period_id': fields.many2one('account.period', 'Period', readonly=True),
    }

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'product_usage_history_analysis_report')
        cr.execute("""
                create view product_usage_history_analysis_report as (
                    SELECT 
                    * FROM product_usage_history
                )
            """)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
