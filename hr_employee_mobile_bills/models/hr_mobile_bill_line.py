from openerp import models, fields
from openerp import api


class HrEmpMobileBillLine(models.Model):
    _name = 'hr.mobile.bill.line'
    _description = 'HR mobile bill line'    

    bill_amount = fields.Float(string="Bill Amount", required=True)
    amount = fields.Float(string="Exceed Amount", required=True)
    emp_mobile_phone = fields.Char('Mobile Number', required=True)

    """ Relational Fields """

    
    parent_id = fields.Many2one(comodel_name='hr.mobile.bill',ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string="Employee", store=True,ondelete='cascade',
                                  compute='onchange_emp_mobile_phone')
    
    
    _sql_constraints = [
        ('unique_mobile_number', 'unique(parent_id, emp_mobile_phone)',
         'Mobile Number must be unique per bill!'),
    ]
    
    """All function which process data and operation"""
    @api.depends('emp_mobile_phone')
    @api.onchange('emp_mobile_phone', 'bill_amount')
    def onchange_emp_mobile_phone(self):
        for recode in self:
            if recode.emp_mobile_phone:
                mobile = '%' + recode.emp_mobile_phone
                emp = self.env['hr.employee'].search([('mobile_phone','=ilike',mobile)], limit=1)
                if emp:
                    recode.employee_id = emp.id
                    if emp.mob_bill_unlimited:
                        recode.amount = 0
                    elif emp.current_bill_limit < recode.bill_amount:
                        recode.amount = recode.bill_amount - emp.current_bill_limit
                    else:
                        recode.amount = 0

