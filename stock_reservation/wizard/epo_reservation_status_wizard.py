from openerp import api, exceptions, fields, models
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval as eval
import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_round
from openerp import tools

class ConfirmationWizard(models.TransientModel):
    _name="epo.reservation.status.wizard"
    
    analytic_acc_id = fields.Many2one('account.analytic.account', 'Analytic Account',required=True)
    @api.multi
    def print_report(self):
        context = self.env.context
        datas = {'ids': context.get('active_ids', [])}

        res = self.browse(self._ids)
        res = res and res[0] or {}
        ctx = {} 

        
        tools.drop_view_if_exists(self.env.cr,'epo_reservation_status_report')
        analytic_account_id = res.analytic_acc_id.id
        
        sql = '''
            CREATE OR REPLACE VIEW epo_reservation_status_report AS (
             SELECT ROW_NUMBER() OVER(ORDER BY rq.product_id DESC) AS id, rq.analytic_account_id,
             aa.name as epo_no, rq.location,rq.product_id, COALESCE(sum(rq.reserve_quantity),0) as quantity
                 ,concat(p.name_template,' ',pav.name) as product_name, l.name as location_name
                    FROM reservation_quant rq
                LEFT JOIN product_product p on(rq.product_id=p.id)
                LEFT JOIN stock_location l on(rq.location=l.id)
                LEFT JOIN account_analytic_account aa on(rq.analytic_account_id=aa.id)
                LEFT JOIN product_attribute_value_product_product_rel par on(p.id=par.prod_id)
                LEFT JOIN product_attribute_value pav on(par.att_id=pav.id)
                where rq.analytic_account_id = %s 
                Group by rq.analytic_account_id,aa.name,rq.location, 
                        p.name_template, rq.product_id,l.name,pav.name)
        ''' %(analytic_account_id)
        
        """   
        sql = '''
            CREATE OR REPLACE VIEW epo_reservation_status_report AS (
                SELECT ROW_NUMBER() OVER(ORDER BY product_id DESC) AS id, analytic_account_id, epo_no, COALESCE(sum(qty),0) as quantity,
                    product_name, location_name
                    FROM (
                    SELECT sr.analytic_account_id, aa.name as epo_no
                     ,sr.source_loc_id,  sr.analytic_resv_loc_id, COALESCE(sum(srl.quantity),0) as qty
                     , concat(p.name_template,' ',pav.name) as product_name, srl.product_id, l.name as location_name
                        FROM stock_reservation sr
                    LEFT JOIN stock_reservation_line srl on(sr.id=srl.stock_reservation_id)
                    LEFT JOIN product_product p on(srl.product_id=p.id)
                    LEFT JOIN stock_location l on(sr.analytic_resv_loc_id=l.id)
                    LEFT JOIN account_analytic_account aa on(sr.analytic_account_id=aa.id)
                    LEFT JOIN product_attribute_value_product_product_rel par on(p.id=par.prod_id)
                    LEFT JOIN product_attribute_value pav on(par.att_id=pav.id)
                    where sr.state = 'reserve' and sr.allocate_flag = 1 AND sr.analytic_account_id = %s
                    Group by sr.analytic_account_id,aa.name,sr.source_loc_id, 
                        sr.analytic_resv_loc_id, p.name_template, srl.product_id,l.name,pav.name
                    
                    UNION ALL
                    
                    SELECT sr.analytic_account_id, aa.name as epo_no
                     ,sr.source_loc_id, sr.analytic_resv_loc_id, (-1)*COALESCE(sum(srl.quantity),0) as qty
                     , concat(p.name_template,' ',pav.name) as product_name, srl.product_id, l.name as location_name
                        FROM stock_reservation sr
                    LEFT JOIN stock_reservation_line srl on(sr.id=srl.stock_reservation_id)
                    LEFT JOIN product_product p on(srl.product_id=p.id)
                    LEFT JOIN stock_location l on(sr.source_loc_id=l.id)
                    LEFT JOIN account_analytic_account aa on(sr.analytic_account_id=aa.id)
                    LEFT JOIN product_attribute_value_product_product_rel par on(p.id=par.prod_id)
                    LEFT JOIN product_attribute_value pav on(par.att_id=pav.id)
                    where sr.state = 'release' and sr.allocate_flag = 2 AND sr.analytic_account_id = %s
                    Group by sr.analytic_account_id,aa.name,sr.source_loc_id,
                        sr.analytic_resv_loc_id, p.name_template,srl.product_id,l.name,pav.name
                    
                    UNION ALL
                    
                    SELECT sr.analytic_account_id, aa.name as epo_no
                     ,sr.source_loc_id,sr.analytic_resv_loc_id, COALESCE(sum(srl.quantity),0) as qty
                     , concat(p.name_template,' ',pav.name) as product_name, srl.product_id, l.name as location_name
                        FROM stock_reservation sr
                    LEFT JOIN stock_reservation_line srl on(sr.id=srl.stock_reservation_id)
                    LEFT JOIN product_product p on(srl.product_id=p.id)
                    LEFT JOIN stock_location l on(sr.source_loc_id=l.id)
                    LEFT JOIN account_analytic_account aa on(sr.analytic_account_id=aa.id)
                    LEFT JOIN product_attribute_value_product_product_rel par on(p.id=par.prod_id)
                    LEFT JOIN product_attribute_value pav on(par.att_id=pav.id)
                    where sr.state = 'release' and sr.allocate_flag = 3 AND sr.analytic_account_id = %s
                    Group by sr.analytic_account_id,aa.name,sr.source_loc_id,
                        sr.analytic_resv_loc_id, p.name_template,srl.product_id,l.name,pav.name
                    ) AS reserve_tble GROUP BY analytic_account_id, epo_no,
                         product_name,product_id,location_name  )
        ''' %(analytic_account_id,analytic_account_id,analytic_account_id)
        """
        print '------sql--------',sql
        self.env.cr.execute(sql)
        print '------sql--------',sql
        return {
            'name': ('EPO Reservation Status Report'),
            'view_type': 'form',
            'view_mode': 'tree,graph',
            'res_model': 'epo.reservation.status.report',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'data':ctx
            
        }
