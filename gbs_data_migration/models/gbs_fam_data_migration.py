
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class GBSFamDataMigration(models.Model):
    _name = 'gbs.fam.data.migration'
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _description = "Import File"
    _rec_name = 'code'
    _order = 'id desc'

    code = fields.Char(string='Code', track_visibility='onchange', readonly=True)
    date = fields.Date(string='Date', default=fields.Datetime.now, track_visibility='onchange')

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'processed':
                raise ValidationError(_('Processed record can not be deleted.'))
        return super(GBSFamDataMigration, self).unlink()

