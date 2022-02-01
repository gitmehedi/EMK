from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import xlrd
import csv
import base64
from datetime import datetime
from odoo.tools import ustr
from collections import OrderedDict

class HrPayrollArrearImportWizard(models.TransientModel):
    _name = 'hr.payroll.arrear.import.wizard'

    file = fields.Binary(string="File", required=True)
    fname = fields.Char(string='Filename')




    def _default_arrear_id(self):
        arrear_id = self.env['hr.payroll.arrear'].browse(self.env.context.get(
            'active_id'))
        return arrear_id

    arrear_id = fields.Many2one(
        'hr.payroll.arrear',
        default=lambda self: self._default_arrear_id(),
        string='Arrear',
        required=True
    )

    def _default_description(self):
        arrear_id = self.env['hr.payroll.arrear'].browse(self.env.context.get(
            'active_id'))
        return arrear_id.name

    name = fields.Char(string="Description", default=lambda self: self._default_description(), readonly=True)

    def _default_company(self):
        arrear_id = self.env['hr.payroll.arrear'].browse(self.env.context.get(
            'active_id'))
        return arrear_id.company_id.id

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self._default_company(),
                                 readonly=True)

    def _default_operating_unit(self):
        arrear_id = self.env['hr.payroll.arrear'].browse(self.env.context.get(
            'active_id'))
        return arrear_id.operating_unit_id.id

    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        default=lambda self: self._default_operating_unit(), readonly=True)


    def save_line_data(self, values):
        # ('values format', [[u'', '1511', '867'],[u'', '1511', '867']])
        arrear_line_obj = self.env['hr.payroll.arrear.line']
        errors = []
        for val in values:
            employee_obj = self.env['hr.employee'].search([('device_employee_acc', '=', int(val[1]))])
            # checking active employee
            if not employee_obj.resource_id.active:
                errors.append(
                    'AC NO : ' + str(int(val[1])) + ', Error : Wrong Employee in excel! You '
                                                                         'cannot upload archived employee data!')

            # checking selected operating unit employee
            if employee_obj.operating_unit_id.id != self.operating_unit_id.id:
                errors.append(
                    'AC NO : ' + str(int(val[1])) + ', Error : Wrong Employee in excel! You can '
                                                                         'only upload selected Operating Unit '
                                                                         'Employee!')

            if employee_obj:
                self._cr.execute('''
                        SELECT id FROM hr_payroll_arrear_line
                                WHERE employee_id=%s 
                                        AND parent_id=%s
                                    ''' % (employee_obj.id, self.arrear_id.id))

                results = self._cr.fetchall()
                if results:
                    for record in results:
                        # checking already uploaded employee
                        if record:
                            errors.append(
                                'AC NO : ' + str(int(val[1])) + ', Error : Employee already uploaded!')
                        else:
                            arrear_line_obj.create({
                                'arear_amount': int(val[2]),
                                'parent_id': self.arrear_id.id,
                                'employee_id': employee_obj.id,
                                'operating_unit_id': self.operating_unit_id.id,
                                'company_id': self.company_id.id,
                                'device_employee_acc': int(val[1]),
                                'state': 'draft'
                            })

                else:
                    arrear_line_obj.create({
                        'arear_amount': int(val[2]),
                        'parent_id': self.arrear_id.id,
                        'employee_id': employee_obj.id,
                        'operating_unit_id': self.operating_unit_id.id,
                        'company_id': self.company_id.id,
                        'device_employee_acc': int(val[1]),
                        'state': 'draft'
                    })

        if errors:
            error_msg = ''
            for error in errors:
                error_msg = error_msg + "\n" + error
            raise UserError(error_msg)

        return True


    @api.multi
    def arrear_import(self):
        if self and self.file:
            try:
                values = []
                values = self.env['gbs.read.excel.utility'].read_xls_book(self.file)
                vals = {
                    'arrear_id': self.arrear_id.id,
                }
                if self.save_line_data(values):
                    message_id = self.env['arrear.success.wizard'].create({'message': _(
                        "Arrear Created Successfully!")
                    })
                    return {
                        'name': _('Success'),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'arrear.success.wizard',
                        'context': vals,
                        'res_id': message_id.id,
                        'target': 'new'
                    }
                else:
                    message_id = self.env['arrear.success.wizard'].create({'message': _(
                        "Arrear Creation Failed!")
                    })
                    return {
                        'name': _('Failure'),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'arrear.success.wizard',
                        'context': vals,
                        'res_id': message_id.id,
                        'target': 'new'
                    }

            except Exception as e:
                raise UserError(_("Arrear Uploading Failed!" + ustr(e)))
