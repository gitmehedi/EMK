from openerp import api, exceptions, fields, models

class SampleRequisition(models.Model):
	_name = 'sample.requisition'
	_defaults = {
			'name': lambda obj, cr, uid,
			context: obj.pool.get('ir.sequence').get(cr, uid, 'sample.requisition'),
			}
	
	
	name = fields.Char(required=True, string="Serial No", readonly=True)
	ref_no = fields.Char(string='Reference No', size=30, readonly=True,
						states={'draft':[('readonly', False)]})
	quantity = fields.Float(size=6, digits=(14, 2), string='Quantity', readonly=True, required=True,
						states={'draft':[('readonly', False)]})
	unit_price = fields.Float(digits=(6, 2), string='Unit Price', readonly=True,
							states={'draft':[('readonly', False)]})
	req_instruction = fields.Text(string='Instruction', readonly=True,
								states={'draft':[('readonly', False)]})
	
	# Relational Fields
	
	buyer_id = fields.Many2one('res.partner', string="Buyer", required=True,
							ondelete='set null', domain=[('customer', '=', True)],
							readonly=True, states={'draft':[('readonly', False)]})
	style_id = fields.Many2one('product.style', string="Style", readonly=True, required=True,
							states={'draft':[('readonly', False)]})  
	sample_type = fields.Many2one('res.sample.type', string="Sample Type", readonly=True, required=True,
								states={'draft':[('readonly', False)]}) 
	work_type = fields.Many2one('res.work.type', string="Work Type", readonly=True, required=True,
							states={'draft':[('readonly', False)]})
	uom = fields.Many2one('product.uom', string="UOM", ondelete='set null', readonly=True, required=True,
						states={'draft':[('readonly', False)]}, domain=[('category_id', '=', 'Unit')])
	currency = fields.Many2one('res.currency', string="Currency", ondelete='set null', readonly=True,
							states={'draft':[('readonly', False)]})
	assigned_id = fields.Many2one('res.users', string="Assigned/Attention", ondelete='set null', readonly=True,
								states={'draft':[('readonly', False)]},domain=[('merchandiser', '=', True)],)
	raw_material_source = fields.Many2one('res.raw.material.source', string="Source", readonly=True,
										states={'draft':[('readonly', False)]})
	state = fields.Selection([('draft', "Draft"), ('confirmed', "Confirmed"), ('development', "Development"),
							 ('received', "Received"), ('submission', "Submission"), ('cancelled', "Cancelled"), ('done', "Done")],
							default="draft", readonly=True, track_visibility='onchange')
	
	# One2many relationship
	sample_development_ids = fields.One2many('sample.development.request', 'sample_requisition_id',
											string="Sample Development", readonly=True)
 	sample_development_rec_ids = fields.One2many('sample.development.receive', 'sample_requisition_id',
 											string="Sample Development Receive", readonly=True)
 	sample_development_sub_ids = fields.One2many('sample.development.submission', 'sample_requisition_id',
 											string="Sample Development Submission", readonly=True)
	
	_sql_constraints = [
        ('sample_requisition_unique_no', 'unique(name)', 'Sample Requisition Name Must Be Unique.'),
        ('check_quantity', "CHECK(quantity > 0.00)", "Quantity must be greater than zero..")
    ]
	
	
	"""
	On Change functionality
	"""
	@api.onchange('buyer_id')
	def _onchange_buyer_id(self):
		self.style_id = 0
    
	
	@api.one
	def action_draft(self):
		self.state = 'draft'

	@api.one
	def action_confirm(self):
		self.state = 'confirmed'
	
	@api.one
	def action_redevelopment(self):
		self.state = 'development'
	
	@api.one
	def action_submission(self):
		self.state = 'submission'

	@api.one
	def action_done(self):
		self.state = 'done'
	
	@api.one
	def action_cancel(self):
		self.state = 'cancelled'
		
	@api.multi    
	def action_development(self, context=None):
		return {
		    'name': ('Create Sample Development'),
		    'view_type': 'form',
		    'view_mode': 'form',
		    'src_model': 'sample.requisition',
		    'res_model': 'sample.development.request.wizard',
		    'view_id': False,
		    'type': 'ir.actions.act_window',
		    'target':'new',
		}
		
	@api.multi    
	def action_receive(self, context=None):
		return {
		    'name': ('Sample Development Receive'),
		    'view_type': 'form',
		    'view_mode': 'form',
		    'src_model': 'sample.requisition',
		    'res_model': 'sample.development.receive.wizard',
		    'view_id': False,
		    'type': 'ir.actions.act_window',
		    'target':'new',
		}
		
	@api.multi    
	def action_submission(self, context=None):
		return {
		    'name': ('Sample Development Submission'),
		    'view_type': 'form',
		    'view_mode': 'form',
		    'src_model': 'sample.requisition',
		    'res_model': 'sample.development.submission.wizard',
		    'view_id': False,
		    'type': 'ir.actions.act_window',
		    'target':'new',
		}
