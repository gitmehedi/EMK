from odoo import models, fields,_
from odoo.exceptions import UserError, ValidationError
from odoo import api


class HrMobileBill(models.Model):
    _name = 'hr.mobile.bill'
    _inherit = ['mail.thread']
    _order = 'state desc'
    _description = 'Employee Mobile Bill'
    _rec_name = 'name'

    name = fields.Char(size=100, string="Name", required=True,states={'draft': [('invisible', False)],
            'applied': [('readonly', True)], 'approved':[('readonly', True)]})
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.user.company_id)

    """ All relations fields """
    line_ids = fields.One2many(comodel_name='hr.mobile.bill.line',inverse_name='parent_id', string="Line Ids", readonly=True,copy=True,
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
                line.write({'state': 'applied'})
    
    @api.multi
    def action_done(self):
        self.state = 'approved'
        for line in self.line_ids:
            if line.state != 'adjusted':
                line.write({'state': 'approved'})

    # @api.constrains('name')
    # def _check_unique_constraint(self):
    #     if self.name:
    #         filters = [['name', '=ilike', self.name]]
    #         name = self.search(filters)
    #         if len(name) > 1:
    #             raise Warning('[Unique Error] Name must be unique!')

    @api.multi
    def unlink(self):
        for bill in self:
            if bill.state != 'draft':
                raise UserError(_('After Approval you can not delete this record.'))
            bill.line_ids.unlink()
        return super(HrMobileBill, self).unlink()