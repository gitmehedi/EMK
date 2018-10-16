from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EventReservationForm(models.Model):
    _name = 'event.reservation.form'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'organizer_id'

    organizer_id = fields.Many2one('res.partner', string='Organizer Name', domain=[('organizer', '=', True)],
                                   default=False)
    event_type_id = fields.Many2one('event.type', string='Event Type')
    space_id = fields.Many2one('event.room', string='Emk Space Requested')
    payment_mode = fields.Selection([('cash', 'Cash'),('cheque', 'cheque')],string="Mode of Payment")
    org_type = fields.Char(string="Organization Type")
    contract_number = fields.Char(string="Contract Number", readonly=True,
                                  related='organizer_id.mobile')
    work_email = fields.Char(string="Email", readonly=True, related='organizer_id.email')
    attendee_number = fields.Char('Estimated Number of Attendees')
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    request_date = fields.Datetime(string='Requested Date')
    payment_date = fields.Datetime(string='Expected Date for Payment')
    event_description = fields.Text('Description', track_visibility='onchange')
    rules = fields.Text('Rules & regulation', track_visibility='onchange')
    comment = fields.Text('Comments', track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'),('on_process', 'On Process'),('confirm', 'Confirmed'), ('done', 'Close'),
                              ('cancel', 'Canceled')], string="State", default="draft", track_visibility='onchange')
