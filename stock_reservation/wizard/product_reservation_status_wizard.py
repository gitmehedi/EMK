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
            SELECT sr.id AS id, sr.analytic_account_id, aa.name as epo_no, sr.analytic_resv_loc_id
                 ,sr.source_loc_id,sr.warehouse_id, sr.state
                 ,srl.destination_loc_id,srl.product_id, srl.quantity
                 , p.name_template as name, l.name as location_name
                    FROM stock_reservation sr
                LEFT JOIN stock_reservation_line srl on(sr.id=srl.stock_reservation_id)
                LEFT JOIN product_product p on(srl.product_id=p.id)
                LEFT JOIN stock_location l on(srl.destination_loc_id=l.id)
                LEFT JOIN account_analytic_account aa on(sr.analytic_account_id=aa.id)
                where sr.state = 'reserve' AND srl.product_id = %s )
        ''' %(product_id)
        print '------sql--------',sql
        self.env.cr.execute(sql)
        print '------sql--------',sql
        return {
            'name': ('Product Reservation Status Report'),
            'view_type': 'form',
            'view_mode': 'tree,graph',
            'res_model': 'product.reservation.status.report',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'data':ctx
            
        }
