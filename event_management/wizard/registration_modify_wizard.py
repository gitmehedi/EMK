from odoo import _, api, models, fields


class WizardMonthlyEvent(models.TransientModel):
    _name = "registration.modify.wizard"

    last_date_reg = fields.Datetime(string='Expected Registration Date')
    close_registration = fields.Selection([('open', 'Open'), ('close', 'Close')], string='Close Registration')

    @api.multi
    def act_registration(self):
        event = self.env['event.event'].browse(self._context['active_id'])
        vals = {}
        if self.last_date_reg:
            vals['last_date_reg'] = self.last_date_reg
        if self.close_registration:
            vals['close_registration'] = self.close_registration

        event.write(vals)

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'src_model': 'event.event',
            'res_model': 'event.event',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': event.id
        }
