from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PackOperation(models.Model):
    _inherit = "stock.pack.operation"

    @api.constrains('qty_done')
    def _check_qty_done(self):
        if self.qty_done > self.product_qty and not self.product_id.receive_over_ok:
            raise ValidationError(_('You can not give bigger value then required value!!'))
        elif self.qty_done < 0:
            raise ValidationError(_('You can not give negative value!!'))



