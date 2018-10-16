from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventReservation(models.Model):
    _name = 'event.reservation'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'organizer_id'

    name = fields.Char(string='Name', readonly=True, states={'draft': [('readonly', False)]})

    organizer_id = fields.Many2one('res.partner', string='Organizer Name', domain=[('organizer', '=', True)],
                                   default=False, required=True, track_visibility='onchange',
                                   readonly=True, states={'draft': [('readonly', False)]})
    event_type_id = fields.Many2one('event.type', string='Event Type', required=True, track_visibility='onchange',
                                    readonly=True, states={'draft': [('readonly', False)]})
    payment_mode = fields.Selection([('cash', 'Cash'), ('cheque', 'cheque')], string="Mode of Payment", required=True,
                                    track_visibility='onchange',
                                    readonly=True, states={'draft': [('readonly', False)]})
    org_type_id = fields.Many2one('event.organization.type',string="Organization Type", required=True, track_visibility='onchange',
                           readonly=True, states={'draft': [('readonly', False)]})
    contract_number = fields.Char(string="Contract Number", readonly=True, related='organizer_id.mobile')
    work_email = fields.Char(string="Email", readonly=True, related='organizer_id.email')
    attendee_number = fields.Char('Estimated Number of Attendees', required=True, track_visibility='onchange',
                                  readonly=True, states={'draft': [('readonly', False)]})
    start_date = fields.Datetime(string='Start Date', required=True, track_visibility='onchange',
                                 readonly=True, states={'draft': [('readonly', False)]})
    end_date = fields.Datetime(string='End Date', required=True, track_visibility='onchange',
                               readonly=True, states={'draft': [('readonly', False)]})
    request_date = fields.Datetime(string='Requested Date', required=True, track_visibility='onchange',
                                   readonly=True, states={'draft': [('readonly', False)]})
    payment_date = fields.Datetime(string='Expected Date for Payment', required=True, track_visibility='onchange',
                                   readonly=True, states={'draft': [('readonly', False)]})
    event_description = fields.Text('Description', track_visibility='onchange', required=True,
                                    readonly=True, states={'draft': [('readonly', False)]})
    rules = fields.Text('Rules & regulation', track_visibility='onchange', required=True,
                        readonly=True, states={'draft': [('readonly', False)]})
    comment = fields.Text('Comments', track_visibility='onchange', required=True,
                          readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection(
        [('draft', 'Draft'), ('on_process', 'On Process'), ('confirm', 'Confirmed'), ('done', 'Close'),
         ('cancel', 'Canceled')], string="State", default="draft", track_visibility='onchange')

    @api.one
    def act_draft(self):
        if self.state == 'on_process':
            self.state = 'draft'

    @api.one
    def act_on_process(self):
        if self.state == 'draft':
            self.name = self.env['ir.sequence'].next_by_code('event.reservation')
            self.state = 'on_process'

    @api.one
    def act_confirm(self):
        if self.state == 'on_process':
            self.state = 'confirm'

    @api.one
    def act_done(self):
        if self.state == 'confirm':
            self.state = 'draft'

    @api.one
    def act_cancel(self):
        if self.state == 'draft':
            self.state = 'cancel'
