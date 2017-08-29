# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2015 Salton Massally (<smassally@idtlabs.sl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import api, fields, models, SUPERUSER_ID
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def _get_employee_manager(self):
        res = {}
        """Get Employee Supervisor / Manager / Department Manager."""
        for emp in self:
            manager = []
            #self.ensure_one()
            if emp.parent_id:
                manager.append(emp.parent_id)
            if emp.department_id and emp.department_id.manager_id:
                manager.append(emp.department_id.manager_id)
            res[emp.id] = manager
        return res