from openerp import fields
from openerp import api,models
import datetime

class HrShifting(models.Model):
   # _name = 'hr.shifting'
    _inherit = ['resource.calendar.attendance']
    

    #Fields of Model    
    ot_hour_from = fields.Float(string='OT from')
    ot_hour_to = fields.Float(string='OT to')
    isIncludedOt =  fields.Boolean(string='Is it included OT', default=False)    
    calendar_id = fields.Many2one("resource.calendar", string="Resource's Calendar", required=False)



class HrShifting(models.Model):
    _inherit = ['hr.employee']
    
    #Fields of Model
    current_shift_id = fields.Many2one('resource.calendar', compute='_compute_current_shift', string='Current Shift')    
    #current_shift_id = fields.Many2one("resource.calendar", string="Employee shift")
    shift_ids = fields.One2many('hr.shifting.history', 'employee_id', string='Employee Shift History')
    
    
    @api.multi
    def _compute_current_shift(self):


        query = """SELECT h.shift_id FROM hr_shifting_history h
                                  WHERE h.employee_id = %s
                               ORDER BY h.effective_from DESC
                                  LIMIT 1"""
        for emp in self:
            self._cr.execute(query, tuple([emp.id]))
            res = self._cr.fetchall()
            if res:
                emp.current_shift_id = res[0][0]

    # """All function which process data and operation"""


    # @api.depends('shift_ids')
    # def _compute_end_from(self):
    #     for record in self:
    #         print "--------------only id----------", record.id

            # if (isinstance(record.id, int)):
            #     print "---------------- 1 st Calling -------------------", record.id
            #     shifting = self.env['hr.shifting.history'].search(
            #         [('employee_id', '=', record.employee_id.id),
            #          ('effective_end', '!=', None)], order='id desc', limit=1)
            #
            #     if shifting:
            #         print "---------------- Calling -------------------", shifting.id
            #         effective_from_tmp = int(
            #             datetime.datetime.strptime(record.effective_from, '%Y-%m-%d').strftime("%s"))
            #         effective_end_tmp = datetime.datetime.fromtimestamp(
            #             effective_from_tmp - 86400).strftime('%Y-%m-%d')
            #
            #         for shift in shifting:
            #             shift.effective_end = effective_end_tmp

    # @api.model
    # def create(self, vals):
    #     # shifting = self.env['hr.shifting.history'].search([('employee_id', '=', vals['employee_id'])],
    #     #                                                   order='id desc', limit=1)
    #     # if shifting.id:
    #     #     effective_from_tmp = int(datetime.datetime.strptime(vals['effective_from'], '%Y-%m-%d').strftime("%s"))
    #     #     effective_end_tmp = datetime.datetime.fromtimestamp(effective_from_tmp-86400).strftime('%Y-%m-%d')
    #     #
    #     #     # shiftin10g.write({'effective_end': efftive_end_tmp})
    #     #     shifting.effective_end = effective_end_tmp
    #
    #     return super(HrShifting, self).create(vals)
    # #
    # @api.multi
    # def write(self, vals):
    #
    #     if vals['shift_ids']:
    #         for history in  vals['shift_ids']:
    #             if history[0]==0:
    #                 history[2]['employee_id']= self.id
    #                 history[2]['actual']= True
    #                 self.shift_ids.create(history[2])
    #             elif history[0]==1:
    #                 history[2]['employee_id'] = self.id
    #                 history[2]['actual'] = True
    #                 self.shift_ids.write(history[2])
    #
    #     return super(HrShifting, self).write(vals)
        