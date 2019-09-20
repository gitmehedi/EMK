from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HrEmployeeOtherAllowance(models.Model):
    _name = 'hr.other.allowance'
    _order = 'name desc'

    name = fields.Char(size=100, string="Description", required=True, readonly=True,
                       states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.user.company_id)

    """ All relations fields """
    line_ids = fields.One2many('hr.other.allowance.line', 'parent_id', string="Other Allowance Details", readonly=True,copy= True,
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
                line.write({'state': 'draft'})

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

    @api.multi
    def unlink(self):
        for bill in self:
            if bill.state != 'draft':
                raise UserError(_('After approval you can not delete this record!!'))
            bill.line_ids.unlink()
        return super(HrEmployeeOtherAllowance, self).unlink()

    # @api.constrains('name')
    # def _check_unique_constraint(self):
    #     if self.name:
    #         filters = [['name', '=ilike', self.name]]
    #         name = self.search(filters)
    #         if len(name) > 1:
    #             raise Warning('[Unique Error] Name must be unique!')



