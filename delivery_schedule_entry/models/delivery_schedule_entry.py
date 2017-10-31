from odoo import api, fields, models

import time,datetime

class DeliveryScheduleEntry(models.Model):
    _name = 'delivery.schedule.entry'
    _description = 'Delivery Schedule Entry'
    _inherit = ['mail.thread']

    name = fields.Char(string='Name', index=True, readonly=True)
    sequence_id = fields.Char('Sequence', readonly=True)
    requested_date = fields.Date('Requested Date', default=datetime.date.today(), readonly=True)
    approved_date = fields.Date('Approved Date', default=datetime.date.today(),readonly=True)
    requested_by = fields.Many2one('res.users', string='Requested By', readonly=True, default=lambda self: self.env.user)
    approved_by = fields.Many2one('res.users', string='Approved By', readonly = True)
    line_ids = fields.One2many('delivery.schedule.entry.line', 'parent_id', string="Products", readonly=True,states={'draft': [('readonly', False)]})
    notes = fields.Text('Notes')
    state = fields.Selection([
        ('draft', "Submit"),
        ('approve', "Confirm")
    ], default='draft')

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('delivery.schedule.entry') or '/'
        vals['name'] = seq
        return super(DeliveryScheduleEntry, self).create(vals)
    # @api.one
    # def action_draft(self):
    #     self.state = 'draft'

    # @api.one
    # def action_validate(self):
    #     self.state = 'validate'

    @api.multi
    def action_approve(self):
        self.state = 'approve'
        self.approved_by = self.env.user
        return self.write({'state': 'approve', 'approved_date': time.strftime('%Y-%m-%d %H:%M:%S')})
