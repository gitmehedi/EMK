from odoo import api,models, _
from odoo.exceptions import ValidationError


class InheritedIrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.multi
    def unlink(self):
        if self.res_model == 'sale.order':
            so_obj = self.env['sale.order'].search([('id','=',self.res_id)])
            if so_obj.state == 'done':
                raise ValidationError(_('You can not delete attachments when Sale Order is in Approved stage'))

        return super(InheritedIrAttachment, self).unlink()


