from openerp import fields,api
from openerp import models
import datetime

class HrShifting(models.Model):
    _name = 'hr.shifting.history'
    _order = "effective_from DESC"
   
   
    #Fields of Model
    effective_from = fields.Date(string='Effective Date')
    effective_end = fields.Date(string='Effective End Date')
    employee_id =  fields.Many2one("hr.employee", string='Employee Name', required=True)
    shift_id = fields.Many2one("resource.calendar", string="Shift Name", required=True)
   
   
   
    
    """All function which process data and operation"""
    @api.model
    def create(self,vals):
        shifting = self.env['hr.shifting.history'].search([('employee_id', '=', vals['employee_id'])],
                                                          order='id desc', limit=1)
        if shifting.id:
            effective_from_tmp = int(datetime.datetime.strptime(vals['effective_from'], '%Y-%m-%d').strftime("%s"))
            effective_end_tmp = datetime.datetime.fromtimestamp(effective_from_tmp-86400).strftime('%Y-%m-%d')

            # shifting.write({'effective_end': efftive_end_tmp})
            shifting.effective_end = effective_end_tmp

        return super(HrShifting, self).create(vals)

    # @api.multi
    # def write(self, vals):
    #     shifting = self.env['hr.shifting.history'].search([('employee_id', '=', self.employee_id.id),('effective_end', '!=', None)],
    #                                                       order='id desc', limit=1)
    #     if shifting:
    #         effective_from_tmp = int(datetime.datetime.strptime(vals['effective_from'], '%Y-%m-%d').strftime("%s"))
    #         effective_end_tmp = datetime.datetime.fromtimestamp(effective_from_tmp- 86400).strftime('%Y-%m-%d')
    #
    #         # shifting.effective_end = effective_end_tmp
    #         # shifting.effective_end = effective_end_tmp
    #         # shifting.write({'effective_end':effective_end_tmp})
    #
    #         # return super(HrShifting, self).write(vals)
    #     # return super(HrShifting, self).write(vals)





    # @api.one
    # @api.depends('effective_from')
    # def _compute_effective_end(self):
    #
    #     for record in self:
    #         if not record.effective_end:
    #             record.effective_end = '2018-03-21'
    #         # else:
    #         #     record.total_quantity = 0.00

    #
    # @api.depends('shift_id')
    # @api.onchange('shift_id')
    # def onchange_shift_id(self):
    #     for recode in self:
    #         if recode.shift_id:
    #             emp_pool = self.env['hr.shifting.history'].search([('effective_end','=',None)], limit=1)
    #             # if emp_pool:
    #                 # recode.effective_end = effective_from-1
                