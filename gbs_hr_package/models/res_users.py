# -*- coding: utf-8 -*-
# © 2015-2017 Eficent
# - Jordi Ballester Alomar
# © 2015-2017 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models


class ResUsers(models.Model):

    _inherit = 'res.users'

    @api.multi
    def _get_employee(self):
        emp_pool = self.env['hr.employee']
        for user in self:
            emp_pool.search(['user_id','=',user.id])
            if emp_pool:
                user.employee_id = emp_pool[0].id


    employee_id = fields.Many2one('hr.employee',
                                  'Employee',
                                  compute='_get_employee')
