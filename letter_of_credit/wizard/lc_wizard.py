from odoo import api, fields, models, _
from openerp.addons.commercial.models.utility import Status


class LCNumberWizard(models.TransientModel):
    _name = 'lc.number.wizard'

    name = fields.Char(string="Number", size=100, required=True)

    @api.multi
    def save_number(self):

        form_id = self.env.context.get('active_id')
        lc_form_pool = self.env['letter.credit']
        lc_form_obj = lc_form_pool.search([('id', '=', form_id)])
        lc_form_obj.write(
            {'name': self.name, 'unrevisioned_name': self.name,'state': 'confirmed','last_note': "Getting Bank Confirmation"})
        return {'type': 'ir.actions.act_window_close'}










