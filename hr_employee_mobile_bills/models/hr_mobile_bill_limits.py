from openerp import models, fields, _

class HrMobileBillLimits(models.Model):
    _name = 'hr.mobile.bill.limit'

    name = fields.Char('Name', required=True)
    effective_date = fields.Date('Effective Date', required=True)

    """ Relational Fields """

    line_ids = fields.One2many('hr.employee.mobile.bill.line','parent_id',"Line Ids")

