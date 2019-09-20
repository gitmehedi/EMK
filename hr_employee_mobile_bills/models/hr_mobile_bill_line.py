from odoo import models, fields,_
from odoo import api
from odoo.exceptions import UserError, ValidationError



class HrEmpMobileBillLine(models.Model):
    _name = 'hr.mobile.bill.line'
    _description = 'HR mobile bill line'    

    bill_amount = fields.Float(string="Bill Amount", required=True,
                               readonly= True, states={'draft': [('readonly', False)]})
    amount = fields.Float(string="Exceed Amount", required=True, readonly= True, states={'draft': [('readonly', False)]})
    emp_mobile_phone = fields.Char('Mobile Number', required=True, readonly= True, states={'draft': [('readonly', False)]})

    """ Relational Fields """

    
    parent_id = fields.Many2one(comodel_name='hr.mobile.bill',ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string="Employee", store=True,ondelete='cascade',
                                  compute='onchange_emp_mobile_phone',readonly= True, states={'draft': [('readonly', False)]})

    """ All Selection fields """

    """ All Selection fields """

    state = fields.Selection([
        ('draft', "Draft"),
        ('applied', "Applied"),
        ('approved', "Approved"),
        ('adjusted',"Adjusted")
    ], default='draft')

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

    # Show a msg for minus value
    @api.onchange('bill_amount','amount')
    def _onchange_bill(self):
        if self.bill_amount < 0 or self.amount < 0:
            raise UserError(_('Amount or Exceed Amount never take negative value!'))
