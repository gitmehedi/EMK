from openerp import api, fields, models

class HrEmployee(models.Model):

    _inherit = 'hr.employee'
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit',
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid),
                                      )
class HrDepartment(models.Model):

    _inherit = 'hr.department'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit',
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid),
                                        )

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            name = '%s - %s' % (rec.name, rec.operating_unit_id.name)
            res.append((rec.id, name))
        return res