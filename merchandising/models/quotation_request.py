from openerp import api, exceptions, fields, models

class QuotationRequest(models.Model):
    _name="quotation.request"
    _defaults = {
                'quotation_ref_no': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'quotation.request'),
                }
    
    quotation_ref_no = fields.Char(string="Quotation Ref No", required=True, readonly=True, copy=False)
    buyer_id = fields.Many2one('res.partner', string="Buyer", required=True, ondelete='set null', 
                               domain=[('customer', '=', True)], readonly=True, states = {'draft':[('readonly',False)]})
    style_id = fields.Many2one('product.style', string="Style", required=True,
                                domain=[('visible', '=', 'True'), ('state', '=', 'confirm')],
                                readonly=True, states = {'draft':[('readonly',False)]})
    quotation_request_date = fields.Date(default=fields.Date.today(), string="Request Date", required=True,
                                          readonly=True, states = {'draft':[('readonly',False)]})
    deadline = fields.Date(default=fields.Date.today(), string="Deadline", required=True,
                            readonly=True, states = {'draft':[('readonly',False)]})
    attention_id = fields.Many2one('res.users', string="Attention", required=True,
                                    domain=[('merchandiser', '=', True)],
                                    readonly=True, states = {'draft':[('readonly',False)]})
    state = fields.Selection([('draft', "Draft"), ('confirmed', "Confirmed"), ('submission', "Submission"), ('cancel', "Cancel"), ('done', "Done")],default="draft", readonly=True, track_visibility='onchange')
    _rec_name = 'quotation_ref_no'
    
    quotation_submission_ids = fields.One2many('quotation.submission', 'quotation_request_id', string="Quotation Submission")
    
    _sql_constraints = [
        ('_check_uniq_name_quo_ref', 'unique(quotation_ref_no)', "Quotation Reference No already exists!"),
        ('_check_date_comparison', "CHECK ( (quotation_request_date <= deadline))", "The start date must be lower than end date.")
    ]    
    
    
    @api.one
    def action_draft(self):
        self.state = 'draft'
    
    @api.one
    def action_confirm(self):
        self.state = 'confirmed'
        
    @api.one
    def action_cancel(self):
        self.state = 'cancel'
        
    @api.one
    def action_accepted(self):
        self.state = 'done'

    @api.multi
    def action_resubmission(self, context=None):
        return {
            'name': ('Create Quotation Submission'),
            'view_type': 'form',
            'view_mode': 'form',
            'src_model': 'quotation.request',
            'res_model': 'quotation.submission.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target':'new',
        }
        
    
    @api.multi    
    def action_submission(self, context=None):
        return {
            'name': ('Create Quotation Submission'),
            'view_type': 'form',
            'view_mode': 'form',
            'src_model': 'quotation.request',
            'res_model': 'quotation.submission.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target':'new',
        }
    