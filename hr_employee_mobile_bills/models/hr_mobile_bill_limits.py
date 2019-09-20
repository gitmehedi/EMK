from odoo import models, fields,api, _
from odoo.exceptions import UserError, ValidationError

class HrMobileBillLimits(models.Model):
    _name = 'hr.mobile.bill.limit'
    _inherit = ['mail.thread']
    _order = 'effective_bill_date desc'


    name = fields.Char('Name', required=True,states={'draft': [('invisible', False)],
            'applied': [('readonly', True)], 'approved':[('readonly', True)]})
    effective_bill_date = fields.Date('Effective Date', required=True,states={'draft': [('invisible', False)],
            'applied': [('readonly', True)], 'approved':[('readonly', True)]})
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.user.company_id)

    """ Relational Fields """

    line_ids = fields.One2many('hr.employee.mobile.bill.line','parent_id',"Line Ids",states={'draft': [('invisible', False)],
            'applied': [('readonly', True)], 'approved':[('readonly', True)]})

    """ All Selection fields """

    state = fields.Selection([
        ('draft', "Draft"),
        ('applied', "Applied"),
        ('approved', "Approved"),
    ], default='draft')


    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_confirm(self):
        self.state = 'applied'

    @api.multi
    def action_done(self):
        self.state = 'approved'


    """All function which process data and operation"""
    @api.onchange('effective_bill_date')
    def onchange_effective_bill_date(self):
        if self.effective_bill_date:
            for record in self.line_ids:
                record.effective_date = self.effective_bill_date

    @api.constrains('name')
    def _check_unique_constraint(self):
        if self.name:
            filters = [['name', '=ilike', self.name]]
            name = self.search(filters)
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.multi
    def unlink(self):
        for bill in self:
            if bill.state != 'draft':
                raise UserError(_('After Approval you can not delete this record.'))
            bill.line_ids.unlink()
        return super(HrMobileBillLimits, self).unlink()
