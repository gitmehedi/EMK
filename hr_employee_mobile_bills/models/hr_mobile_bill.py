from openerp import models, fields
import datetime
from openerp import api


class HrEmployeeMobileBill(models.Model):
    _name = 'hr.mobile.bill'
    _order = 'name desc'

    name = fields.Char(size=100, string="Name", required=True,states={'draft': [('invisible', False)],
            'applied': [('readonly', True)], 'approved':[('readonly', True)]})
    

    """ All relations fields """
    line_ids = fields.One2many(comodel_name='hr.mobile.bill.line',inverse_name='parent_id', string="Line Ids")
    
    
    """ All Selection fields """

    state = fields.Selection([
        ('draft', "Draft"),
        ('applied', "Applied"),
        ('approved', "Approved"),
    ], default='draft')
    
    
    
    
    
    """All function which process data and operation"""
    
    @api.multi
    def action_draft(self):
        self.state = 'draft'
    
    @api.multi
    def action_confirm(self):
        self.state = 'applied'
    
    
    @api.multi
    def action_done(self):
        self.state = 'approved'


