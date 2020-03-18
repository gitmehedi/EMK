from odoo import api,models, _
from odoo.exceptions import ValidationError
from datetime import datetime

VALID_DAYS = 185


class InheritedIrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.multi
    def unlink(self):
        date_now = datetime.now()

        for i in self:
            if i.res_model == 'sale.order':
                so_obj = i.env['sale.order'].search([('id', '=', i.res_id)])

                date_create = datetime.strptime(i.create_date, '%Y-%m-%d %H:%M:%S')
                days = (date_now - date_create).days

                if so_obj.state == 'done' and days <= VALID_DAYS:
                    raise ValidationError(_('You can not delete attachments when Sale Order is in Approved stage'))

        return super(InheritedIrAttachment, self).unlink()


