from openerp import fields, models

class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit',
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid))
