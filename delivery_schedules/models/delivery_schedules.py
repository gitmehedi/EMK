import time, datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError



class DeliverySchedules(models.Model):
    _name = 'delivery.schedules'
    _description = 'Delivery Schedule'
    _inherit = ['mail.thread']
    _order = "id DESC"

    name = fields.Char(string='Name', index=True, readonly=True)
    requested_date = fields.Date('Date', default=fields.Datetime.now,readonly=True,
                                 states={'draft': [('readonly', False)]})
    sequence_id = fields.Char('Sequence', readonly=True)
    requested_by = fields.Many2one('res.users', string='Requested By', readonly=True,
                                   default=lambda self: self.env.user)

    ## Sales Person & OP Unit
    #####################################
    @api.model
    def _default_operating_unit(self):
        team = self.env['crm.team']._get_default_team_id()
        if team.operating_unit_id:
            return team.operating_unit_id

    operating_unit_id = fields.Many2one('operating.unit',
                                        string='Operating Unit',
                                        required=True, readonly=True,
                                        default=_default_operating_unit, track_visibility='onchange')

    @api.model
    def _default_sales_team(self):
        team = self.env['crm.team']._get_default_team_id()
        if team:
            return team.id

    sales_team_id = fields.Many2one('crm.team', string='Sales Team', readonly=True,
                                    default=_default_sales_team, track_visibility='onchange')

    ########################################


    line_ids = fields.One2many('delivery.schedules.line', 'parent_id', string="Products", readonly=True,
                               states={'draft': [('readonly', False)]})

    state = fields.Selection([
        ('draft', "Draft"),
        ('approve', "Confirm")
    ], default='draft', track_visibility='onchange')


    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('delivery.schedules') or '/'
        vals['name'] = seq
        return super(DeliverySchedules, self).create(vals)


    @api.multi
    def action_approve(self):

        if self.line_ids:
            self.state = 'approve'
            self.approved_by = self.env.user
            for line in self.line_ids:
                line.write({'state': 'approve',})
            return self.write({'state': 'approve', 'approved_date': time.strftime('%Y-%m-%d %H:%M:%S')})

        raise ValidationError("Without Product Details information, you can't confirm it.")

    @api.multi
    def action_draft(self):
        res = {
            'state': 'draft',
        }
        self.write(res)
        self.line_ids.write({'state': 'draft'})

    @api.multi
    def unlink(self):
        for entry in self:
            if entry.state != 'draft':
                raise UserError(_('After confirmation You can not delete this.'))
            entry.line_ids.unlink()
        return super(DeliverySchedules, self).unlink()


    @api.constrains('name')
    def _check_unique_constraint(self):
        if self.name:
            filters = [['name', '=ilike', self.name]]
            name = self.search(filters)
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.multi
    def generate_schedule_letter(self):

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('delivery_schedules', 'schedule_email_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'delivery.schedules',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "delivery_schedules.schedule_email_template"
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
