from odoo import api,fields, models

class EmpRoster(models.TransientModel):

        _name = 'hr.emp.roster'
        _description = 'Employee Roster'

        operating_unit_id = fields.Many2one('operating.unit', 'Select Operating Unit', required=True,
                                            default=lambda self: self.env.user.default_operating_unit_id)
        department_id = fields.Many2one("hr.department", string="Department", required=False)
        employee_id = fields.Many2one("hr.employee", string="Employee", required=False)
        from_date = fields.Date(string='From Date', required=True)
        to_date = fields.Date(string='To Date', required=True)

        @api.multi
        @api.onchange('operating_unit_id')
        def onchange_operating_unit_id(self):
                if self.operating_unit_id:
                        self.department_id = []
                        query = """SELECT  distinct(department_id) FROM hr_employee WHERE operating_unit_id = %s """
                        self._cr.execute(query, (self.operating_unit_id.id,))
                        res = []
                        for data in self._cr.fetchall():
                                if data[0] != res:
                                        res.append(data[0])

                        return {'domain': {'department_id': [('id', 'in', res)]}}

        @api.multi
        @api.onchange('department_id')
        def onchange_department_id(self):
                if self.department_id:
                        self.employee_id = []
                        query = """SELECT  id FROM hr_employee WHERE department_id = %s AND operating_unit_id = %s"""
                        self._cr.execute(query, (self.department_id.id,self.operating_unit_id.id))
                        res = []
                        for data in self._cr.fetchall():
                                if data[0] != res:
                                        res.append(data[0])

                        return {'domain': {'employee_id': [('id', 'in', res)]}}