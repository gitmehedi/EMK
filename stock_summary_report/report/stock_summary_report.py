# -*- coding: utf-8 -*-
##############################################################################
from openerp import api, models
import datetime
    
class DailyCreditSettlementReport(models.AbstractModel):
    _name = 'report.stock_summary_report.report_stock_summary_qweb'
    
    def _generate_categories(self, category, categories):
        categories.append(category.id)
        for cat in category.child_id:
            categories = self._generate_categories(cat, categories)
        return categories
    
    def _generate_lines(self, warehouse_id, category, from_date, to_date):
        
        categories = []
        categories = self._generate_categories(category, categories)
        # print "======================="
        # print categories
        
        sql_query = """ select ROW_NUMBER() Over (Order by p.id) As serial, p.id, 
                        p.name_template as product_name, c.name as prod_category, u.name as uom, 
                        COALESCE(ph.cost, 0) as cost_price, 
                        (COALESCE(q1.qty, 0)-COALESCE(q2.qty, 0)) as op_qty,
                        COALESCE(q3.qty, 0) as receive_qty, COALESCE(q4.qty, 0) as issue_qty
                        from product_product p
                        left join product_template t on t.id = p.product_tmpl_id
                        left join product_category c on c.id = t.categ_id
                        left join product_uom u on u.id = t.uom_id
                        left join (select t.id, p1.cost from product_template t
                        left join product_price_history p1 on p1.product_template_id = t.id
                        where p1.id in (select max(id) from product_price_history p1
                        group by p1.product_template_id)) ph on ph.id = t.id
                        left join 
                        (select p.id, sum(m.product_uom_qty) as qty, avg(price_unit) as unit_price
                        from product_product p
                        left join stock_move m on p.id = m.product_id
                        left join stock_warehouse w on w.lot_stock_id = m.location_dest_id
                        where w.id = %s
                        and date < %s
                        group by p.id) q1 on q1.id = p.id
                        left join
                        (select p.id, sum(m.product_uom_qty) as qty, avg(price_unit) as unit_price
                        from product_product p
                        left join stock_move m on p.id = m.product_id
                        left join stock_warehouse w on w.lot_stock_id = m.location_id
                        where w.id = %s
                        and date < %s
                        group by p.id) q2 on q2.id = p.id
                        left join
                        (select p.id, sum(m.product_uom_qty) as qty, avg(price_unit) as unit_price
                        from product_product p
                        left join stock_move m on p.id = m.product_id
                        left join stock_warehouse w on w.lot_stock_id = m.location_dest_id
                        where w.id = %s
                        and date between %s and %s
                        group by p.id) q3 on p.id = q3.id
                        left join
                        (select p.id, sum(m.product_uom_qty) as qty, avg(price_unit) as unit_price
                        from product_product p
                        left join stock_move m on p.id = m.product_id
                        left join stock_warehouse w on w.lot_stock_id = m.location_id
                        where w.id = %s
                        and date between %s and %s
                        group by p.id) q4 on p.id = q4.id
                        where c.id in %s
                        order by p.id"""

                          
        params = (warehouse_id, from_date,
                  warehouse_id, from_date,
                  warehouse_id, from_date, to_date, 
                  warehouse_id, from_date, to_date,
                  tuple(categories))
        print "----------------------------------------------------------------"

        print sql_query
        print params

        print "----------------------------------------------------------------"

        self.env.cr.execute(sql_query, params)
        res = self.env.cr.dictfetchall()
        
        return res
    
    @api.multi
    def render_html(self, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('stock_summary_report.report_stock_summary_qweb')
        
        lines = self._generate_lines(docs.warehouse_id.id, docs.category_id,docs.product_id,
                                     docs.start_date, docs.end_date)

        print  lines
        
        docargs = {
            'doc_ids'               : self._ids,
            'doc_model'             : report.model,
            'docs'                  : self,
            'start_date'            : docs.start_date,
            'end_date'              : docs.end_date,
            'category_id'           : docs.category_id.display_name,
            'product_id'            : docs.product_id.name,
            'warehouse_id'          : docs.warehouse_id.name,
            'lines'                 : lines,
        }
        return report_obj.render('stock_summary_report.report_stock_summary_qweb', docargs)
    
