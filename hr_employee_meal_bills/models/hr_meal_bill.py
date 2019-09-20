from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HrEmployeeMealBill(models.Model):
    _name = 'hr.meal.bill'
    _inherit = ['mail.thread']
    _order = 'name desc'
    _description = 'Employee Meal Bill'
    _rec_name = 'name'


    name = fields.Char(size=100, string="Description", required=True, readonly=True,track_visibility='onchange',
                       states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string='Company', index=True, track_visibility='onchange',
                                 default=lambda self: self.env.user.company_id)

    """ All relations fields """
    line_ids = fields.One2many('hr.meal.bill.line', 'parent_id', string="Meal Details",readonly=True,copy=True,
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
        for line in self.line_ids:
            if line.state != 'adjusted':
                line.write({'state':'draft'})
    
    @api.multi
    def action_confirm(self):
        self.state = 'applied'
        for line in self.line_ids:
            if line.state != 'adjusted':
                line.write({'state':'applied'})

    @api.multi
    def action_done(self):
        self.state = 'approved'
        for line in self.line_ids:
            if line.state != 'adjusted':
                line.write({'state':'approved'})

    @api.multi
    def unlink(self):
        for bill in self:
            if bill.state != 'draft':
                raise UserError(_('After Approval You can not delete this record.'))
            bill.line_ids.unlink()
        return super(HrEmployeeMealBill, self).unlink()


