from odoo import api,models, _
from odoo.exceptions import ValidationError


class InheritedIrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.multi
    def unlink(self):
        for i in self:
            if i.res_model == 'sale.order':
                so_obj = i.env['sale.order'].search([('id','=',i.res_id)])
                if so_obj.state == 'done':
                    raise ValidationError(_('You can not delete attachments when Sale Order is in Approved stage'))

        return super(InheritedIrAttachment, self).unlink()


