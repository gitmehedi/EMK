from odoo import api, fields, models, _
from odoo.addons.opa_utility.helper.utility import Message
from odoo.exceptions import ValidationError
from psycopg2 import IntegrityError


class BookingRoom(models.Model):
    _name = 'booking.room'
    _description = "Booking Room"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "id desc"

    name = fields.Char(string='Name', required=True, track_visibility="onchange")
    seat_no = fields.Integer(string="Total Seal",required=True,)
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange')
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange')
    line_ids = fields.One2many('booking.room.line', 'line_id', string='Line')
    type = fields.Selection([('library', 'Library'),
                             ('makerlab', 'MakerLab'),
                             ('golpo_studio', 'Golpo Studio'),
                             ('spondon_studio', 'Spondon Studio'),
                             ],required=True,
                             string='Type', track_visibility='onchange', )
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange', )

    @api.constrains('name')
    def _check_name(self):
        name = self.search(
            [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
             ('active', '=', False)])
        if len(name) > 1:
            raise ValidationError(_(Message.UNIQUE_WARNING))

    @api.onchange("name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ('draft', 'approve', 'reject'))]

    @api.one
    def act_draft(self):
        if self.state == 'reject':
            self.write({
                'state': 'draft',
                'pending': True,
                'active': False,
            })

    @api.one
    def act_approve(self):
        if self.state == 'draft':
            self.write({
                'state': 'approve',
                'pending': False,
                'active': True,
            })

    @api.one
    def act_reject(self):
        if self.state == 'draft':
            self.write({
                'state': 'reject',
                'pending': False,
                'active': False,
            })

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'reject'):
                raise ValidationError(_(Message.UNLINK_WARNING))
            try:
                return super(BookingRoom, rec).unlink()
            except IntegrityError:
                raise ValidationError(_(Message.UNLINK_INT_WARNING))


class BookingRoomLine(models.Model):
    _name = 'booking.room.line'
    _description = "Booking Room"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "id desc"

    name = fields.Char(string='Name', required=True, track_visibility="onchange")
    line_id = fields.Many2one('booking.room', string='Line', ondelete='cascade')
