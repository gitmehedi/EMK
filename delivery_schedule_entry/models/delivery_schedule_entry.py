from odoo import api, fields, models,_
from odoo.exceptions import UserError,ValidationError


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
    notes = fields.Text()
    state = fields.Selection([
        ('draft', "Submit"),
        ('approve', "Confirm")
    ], default='draft')

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('delivery.schedule.entry') or '/'
        vals['name'] = seq
        return super(DeliveryScheduleEntry, self).create(vals)


    @api.multi
    def action_approve(self):
        self.state = 'approve'
        self.approved_by = self.env.user
        return self.write({'state': 'approve', 'approved_date': time.strftime('%Y-%m-%d %H:%M:%S')})

    @api.multi
    def unlink(self):
        for entry in self:
            if entry.state != 'draft':
                raise UserError(_('You can not delete this.'))
            entry.line_ids.unlink()
        return super(DeliveryScheduleEntry, self).unlink()

    @api.constrains('name')
    def _check_unique_constraint(self):
        if self.name:
            filters = [['name', '=ilike', self.name]]
            name = self.search(filters)
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')





            #     @api.multi
#     def action_quotation_send(self):
#         '''
#         This function opens a window to compose an email, with the edi sale template message loaded by default
#         '''
#         self.ensure_one()
#         ir_model_data = self.env['ir.model.data']
#         try:
#             template_id = ir_model_data.get_object_reference('delivery_schedule_entry', 'delivery_schedule_entry_form')[1]
#         except ValueError:
#             template_id = False
#         try:
#             compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
#         except ValueError:
#             compose_form_id = False
#         ctx = dict()
#         ctx.update({
#             'default_model': 'delivery.schedule.entry',
#             'default_res_id': self.ids[0],
#             'default_use_template': bool(template_id),
#             'default_template_id': template_id,
#             'default_composition_mode': 'comment',
#             'mark_so_as_sent': True,
#             'custom_layout': "delivery_schedule_entry.template_delivery_order"
#         })
#         return {
#             'type': 'ir.actions.act_window',
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'mail.compose.message',
#             'views': [(compose_form_id, 'form')],
#             'view_id': compose_form_id,
#             'target': 'new',
#             'context': ctx,
#         }
#
#
# class MailComposeMessage(models.TransientModel):
#     _inherit = 'mail.compose.message'
#
#     @api.multi
#     def send_mail(self, auto_commit=False):
#         if self._context.get('default_model') == 'delivery.schedule.entry' and self._context.get('default_res_id') and self._context.get('mark_so_as_sent'):
#             order = self.env['delivery.schedule.entry'].browse([self._context['default_res_id']])
#             if order.state == 'draft':
#                 order.state = 'approve'
#             self = self.with_context(mail_post_autofollow=True)
#         return super(MailComposeMessage, self).send_mail(auto_commit=auto_commit)