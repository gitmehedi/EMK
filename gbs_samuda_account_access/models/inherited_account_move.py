from odoo import fields, models, api


class InheritedAccountMove(models.Model):
    _inherit = 'account.move'

    submitted_from = fields.Selection([('unit', 'Unit'), ('ho', 'HO')], default='ho')

    def _get_operating_units(self):
        if self.env.context.get('default_submitted_from') == 'unit':
            return [("id", "in", self.env.user.operating_unit_ids.ids)]
        else:
            # only operating unit of allowed company
            operating_units = self.env['operating.unit'].search(
                [('company_id', 'in', self.env.user.company_ids.ids)])
            return [("id", "in", operating_units.ids)]

    operating_unit_id = fields.Many2one('operating.unit',
                                        'Operating Unit',
                                        help="This operating unit will "
                                             "be defaulted in the move lines.", domain=_get_operating_units)
