from openerp import api, fields, models, _
from openerp.exceptions import UserError, ValidationError


class HrEmployeeMealBill(models.Model):
    _name = 'hr.meal.bill'
    _inherit = ['mail.thread']
    _order = 'name desc'

    name = fields.Char(size=100, string="Description", required=True, readonly=True,
                       states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.user.company_id)

    """ All relations fields """
    line_ids = fields.One2many('hr.meal.bill.line', 'parent_id', string="Meal Details",readonly=True,
                               states={'draft': [('readonly', False)]})
    
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
        self.line_ids.write({'state':'draft'})
    
    @api.multi
    def action_confirm(self):
        self.state = 'applied'
        self.line_ids.write({'state':'applied'})

    @api.multi
    def action_done(self):
        self.state = 'approved'
        self.line_ids.write({'state':'approved'})

    @api.multi
    def unlink(self):
        for bill in self:
            if bill.state != 'draft':
                raise UserError(_('You can not delete this.'))
            bill.line_ids.unlink()
        return super(HrEmployeeMealBill, self).unlink()


        

