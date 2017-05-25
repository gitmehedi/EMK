from openerp import models, fields, api

class HrEmployeeIouWizard(models.TransientModel):
    _name = 'hr.employee.iou.wizard'

    repay = fields.Float(string="RePay", required=True)

    @api.multi
    def process_repay(self):
        print ''