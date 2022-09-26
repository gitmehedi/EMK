from odoo import fields, models, api


class Followers(models.Model):
    _inherit = 'mail.followers'

    @api.model
    def create(self, vals):
        if 'res_model' in vals and 'res_id' in vals and 'partner_id' in vals:
            dups = self.env['mail.followers'].search(
                [('res_model', '=', vals.get('res_model')), ('res_id', '=', vals.get('res_id')),
                 ('partner_id', '=', vals.get('partner_id'))])


            if len(dups):
                for p in dups:
                    p.unlink()

        res = super(Followers, self).create(vals)

        return res
