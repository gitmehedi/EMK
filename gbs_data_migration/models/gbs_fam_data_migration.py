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

    @api.multi
    def _fam_date_migration(self):
        assets = self.env['account.asset.asset'].search([('state', '=', 'open')])
        for asset in assets:
            asset_depr = asset.depreciation_line_ids.filtered(lambda x: not x.move_check)
            if asset_depr:
                asset_depr.write({'move_check': True,
                                  'move_posted_check': True,
                                  })
        self.env.cr.execute("""UPDATE account_asset_category SET asset_count=0""")
        self.env.cr.execute("""SELECT count(*),asset_type_id  FROM account_asset_asset GROUP BY asset_type_id""")
        for val in self.env.cr.fetchall():
            self.env.cr.execute("""UPDATE account_asset_category SET asset_count=%s WHERE id=%s""" % (val[0], val[1]))

    @api.multi
    def _api_call(self):
        api = self.env['payment.instruction'].search([('state', '=', 'draft')])
        for line in api:
            line.write({'state': 'approved', 'is_sync': True})
