
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

class GBSCOADataMigration(models.Model):
    _name = 'gbs.coa.data.migration'
    _order = 'id desc'

    date = fields.Date(string='Date', default=fields.Datetime.now)

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'processed':
                raise ValidationError(_('Processed record can not be deleted.'))
        return super(GBSCOADataMigration, self).unlink()

