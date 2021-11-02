import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round


class DeliverySchedules(models.Model):
    _name = 'delivery.schedules'
    _description = 'Delivery Schedule'
    _inherit = ['mail.thread']
    _order = "id DESC"

    name = fields.Char(string='Name', default='/', readonly=True)
    revision = fields.Integer(string='Revision', readonly=True, help="Used to keep track of changes")
    origin = fields.Char('Origin', copy=False, help="Origin Name of the document.")
    requested_date = fields.Date('Date', default=fields.Datetime.now, readonly=True, track_visibility='onchange',
                                 states={'draft': [('readonly', False)]})
    requested_by = fields.Many2one('res.users', string='Requested By', readonly=True,
                                   default=lambda self: self.env.user)
    approve_date = fields.Datetime('Approve Date', readonly=True, track_visibility='onchange')
    approved_by = fields.Many2one('res.users', string='Approver', readonly=True,
                                  help="who have approve.", track_visibility='onchange')
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', required=True, readonly=True,
                                        states={'draft': [('readonly', False)]}, track_visibility='onchange')
    scheduled_qty = fields.Float(string='Total Scheduled Qty.', compute='_compute_scheduled_qty', store=True,
                                 track_visibility='onchange')
    region_type = fields.Selection([('local', 'Local'), ('foreign', 'Foreign')], string="Region Type", required=True,
                                   readonly=True, default=lambda self: self.env.context.get('region_type'))
    state = fields.Selection([
        ('draft', "Draft"),
        ('revision', "Revised"),
        ('approve', "Confirm"),
        ('done', "Done")
    ], default='draft', track_visibility='onchange')

    # relational field
    line_ids = fields.One2many('delivery.schedules.line', 'schedule_id', string="Delivery Schedule Line")

    @api.depends('line_ids.scheduled_qty')
    def _compute_scheduled_qty(self):
        for rec in self:
            rec.scheduled_qty = sum(line.scheduled_qty for line in rec.line_ids)

    @api.constrains('requested_date')
    def _check_requested_date(self):
        if self.requested_date < fields.Date.today():
            raise ValidationError(_("Requested date can't be back date entry"))
        if self.requested_date > fields.Date.to_string(datetime.date.today() + relativedelta(days=7)):
            raise ValidationError(_("Requested date can't bigger then 7 days"))

    @api.constrains('line_ids')
    def _check_line_ids(self):
        message = ''
        delivery_orders = self.line_ids.mapped('delivery_order_id')
        for delivery_order in delivery_orders:
            line = self.line_ids.search([('delivery_order_id', '=', delivery_order.id)], limit=1)
            delivery_schedules_lines = self.env['delivery.schedules.line'].search([
                ('delivery_order_id', '=', delivery_order.id),
                ('state', '!=', 'done')
            ])
            total_scheduled_qty = float_round(sum(line.scheduled_qty for line in delivery_schedules_lines), precision_digits=4)
            total_ordered_qty = float_round(delivery_order.line_ids[0].quantity, precision_digits=4)
            total_delivered_qty = float_round(delivery_order.line_ids[0].qty_delivered, precision_digits=4)

            if total_ordered_qty < (total_delivered_qty + total_scheduled_qty):
                message += _('\nSale Order: %s\nUndelivered Qty: %s\nScheduled Qty: %s\n') % (line.sale_order_id.name, line.undelivered_qty, total_scheduled_qty)

        if message:
            raise ValidationError(_('Scheduled qty cannot be greater than Undelivered Qty.\n') + message)

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        self.line_ids = []

    @api.multi
    def unlink(self):
        if any(rec.state != 'draft' for rec in self):
            raise UserError(_('You cannot delete a record which is not in draft state!'))
        if any(rec.line_ids.filtered(lambda x: x.state == 'done') for rec in self):
            raise UserError(_('You cannot delete a record which lines are in done state!'))

        self.mapped('line_ids').unlink()

        return super(DeliverySchedules, self).unlink()

    @api.multi
    def action_confirm(self):
        if not self.line_ids:
            raise ValidationError("Without Product Details information, you can't confirm it.")

        lines = self.line_ids.filtered(lambda i: i.state in ['draft', 'revision'])
        lines.write({'state': 'approve', 'requested_date': self.requested_date})

        vals = {
            'state': 'approve',
            'approve_date': fields.Datetime.now(),
            'approved_by': self.env.user.id,
        }

        if self.name == '/':
            code = self.env['ir.sequence'].next_by_code_new('delivery.schedule', self.requested_date, self.operating_unit_id)
            vals['name'] = code
            vals['origin'] = code

        return self.write(vals)

    @api.multi
    def action_revise(self):
        lines = self.line_ids.filtered(lambda i: i.state != 'done')
        lines.write({'state': 'revision'})

        return self.write({
            'name': self.origin + '/' + str(self.revision + 1),
            'state': 'revision',
            'revision': self.revision + 1,
        })

    @api.multi
    def action_process_delivery_schedules(self):
        """Scheduler method for updating Delivery Schedules State."""
        delivery_schedules = self.env['delivery.schedules'].search([
            ('requested_date', '<=', fields.Datetime.now()),
            ('state', '=', 'approve')
        ])
        for ds in delivery_schedules:
            if any(line.state not in ['done', 'cancel'] for line in ds.line_ids):
                continue

            ds.write({'state': 'done'})
