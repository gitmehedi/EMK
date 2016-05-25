from openerp import api, exceptions, fields, models
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval as eval
import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_round
from openerp import tools

class ConfirmationWizard(models.TransientModel):
    _name="product.reservation.status.wizard"
    
    product_id = fields.Many2one('product.product', string="Product", required=True)
    
    @api.multi
    def print_report(self):
        context = self.env.context
        datas = {'ids': context.get('active_ids', [])}

        res = self.browse(self._ids)
        res = res and res[0] or {}
        ctx = {} 

        
        tools.drop_view_if_exists(self.env.cr,'product_reservation_status_report')
        product_id = res.product_id.id
        
          
        sql = '''
            CREATE OR REPLACE VIEW product_reservation_status_report AS (
             SELECT ROW_NUMBER() OVER(ORDER BY rq.product_id DESC) AS id, rq.analytic_account_id,
             aa.name as epo_no, rq.location,rq.product_id, COALESCE(sum(rq.reserve_quantity),0) as quantity
                 ,concat(p.name_template,' ',pav.name) as product_name, l.name as location_name
                    FROM reservation_quant rq
                LEFT JOIN product_product p on(rq.product_id=p.id)
                LEFT JOIN stock_location l on(rq.location=l.id)
                LEFT JOIN account_analytic_account aa on(rq.analytic_account_id=aa.id)
                LEFT JOIN product_attribute_value_product_product_rel par on(p.id=par.prod_id)
                LEFT JOIN product_attribute_value pav on(par.att_id=pav.id)
                where rq.product_id = %s 
                Group by rq.analytic_account_id,aa.name,rq.location, 
                        p.name_template, rq.product_id,l.name,pav.name)
        ''' %(product_id)
        
        self.env.cr.execute(sql)
        
        return {
            'name': ('Product Reservation Status Report'),
            'view_type': 'form',
            'view_mode': 'tree,graph',
            'res_model': 'product.reservation.status.report',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'data':ctx
            
        }
