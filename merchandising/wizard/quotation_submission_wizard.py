from openerp import api, exceptions, fields, models
from openerp import _
from openerp.exceptions import Warning
"""from openerp.osv import osv
from openerp.exceptions import except_orm
from openerp.tools.translate import _
"""
class QuotationSubmissionWizard(models.TransientModel):
    _name="quotation.submission.wizard"
    
    submission_date = fields.Date(default=fields.Date.today(), string="Submission Date", required=True)
    product_costing_id = fields.Many2one('product.costing', string="Product Costing", required=True, domain=[('product_costing_visible', '=', 'True'),('state', '=', 'approve')])
    remarks = fields.Text(string="Remarks")
    
       
    # create a function that will save the info from your wizard into your model (active_id is the id of the record you called the wizard from, so you will save the info entered in wizard is that record)
    def action_submit(self, cr, uid, ids, context=None):
        print '...........23......'
        req_obj = self.pool.get('quotation.request')
        sub_obj = self.pool.get('quotation.submission')
        req_id = context.get('active_id', False)
        req = req_obj.browse(cr, uid, req_id, context=context)

        for data in self.browse(cr, uid, ids):
            if not req.quotation_request_date <= data.submission_date:    
                raise Warning(_('Submission Date can not be less than Quotation Request Date.'))
                #raise osv.except_osv(_('Error!'), _("Submission Date can not be less than Quotation Request Date."))
            else:
                vals = {
                        'submission_date': data.submission_date,
                        'quotation_request_id':req_id,
                        'product_costing_id': data.product_costing_id.id,
                        'remarks':data.remarks
                        }
                res = sub_obj.create(cr, uid, vals, context=context)
                req_obj.write(cr, uid, [req_id], {'state':'submission'}, context=context)
                
                return {
                    'type': 'ir.actions.act_window_close',
                }
