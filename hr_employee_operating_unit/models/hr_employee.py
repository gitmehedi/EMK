from openerp import api, fields, models

class HrEmployee(models.Model):

    _inherit = 'hr.employee'
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit',
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid),
                                      )
