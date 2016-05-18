from openerp import models, fields, api

class HrHolidaysExtended(models.Model):
       _inherit = 'hr.holidays'

       name= fields.Text(string='Description')

       officer_id = fields.Many2one('res.users', string='HR Officer', compute = '_get_officer_id', store=True)

       state = fields.Selection([('draft', 'To Submit'), ('cancel', 'Cancelled'),('confirm', 'To Approve'), ('refuse', 'Refused'), ('validate1', 'Second Approval'), ('validate', 'Approved')],
            'Status', readonly=True, copy=False, default='draft',
            help='The status is set to \'To Submit\', when a holiday request is created.\
            \nThe status is \'To Approve\', when holiday request is confirmed by user.\
            \nThe status is \'Refused\', when holiday request is refused by manager.\
            \nThe status is \'Approved\', when holiday request is approved by manager.')
       
       @api.depends('employee_id')
       def _get_officer_id(self):
           if(self.employee_id.parent_id):
               self.officer_id = self.employee_id.parent_id.user_id.id
        
        