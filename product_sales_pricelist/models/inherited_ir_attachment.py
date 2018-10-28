from odoo import api,models, _
from odoo.exceptions import ValidationError


class InheritedIrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.multi
    def unlink(self):
        if self.res_model == 'product.sales.pricelist':
            so_obj = self.env['product.sales.pricelist'].search([('id','=',self.res_id)])
            if so_obj.state == 'validate':
                raise ValidationError(_('You can not delete attachment (s) when Price List is in Approved stage'))

        return super(InheritedIrAttachment, self).unlink()


