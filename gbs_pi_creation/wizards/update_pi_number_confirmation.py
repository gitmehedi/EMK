from odoo import api, fields, models, _
from odoo.exceptions import UserError

class UpdatePINumberConfirmation(models.TransientModel):
    _name = 'update.pi.number.confirmation'

    pi_number = fields.Char(string='New PI Number')
    current_pi_number = fields.Char(string='Current LC Number', readonly=True)

    def action_update_pi_number(self):
        pi_id = self._context['pi_id']
        check_proforma_obj = self.env['proforma.invoice'].search([('name', '=', self.pi_number)])
        if check_proforma_obj:
            raise UserError(_("PI number must be unique"))

        proforma_invoice_obj = self.env['proforma.invoice'].browse(pi_id)
        proforma_invoice_obj.write({'name': self.pi_number})