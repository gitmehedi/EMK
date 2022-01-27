from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import xlrd
import csv
import base64
from datetime import datetime
from odoo.tools import ustr
from collections import OrderedDict


class HrEmployeeMealBillsImportWizard(models.TransientModel):
    _name = 'hr.employee.meal.bills.import.wizard'

    file = fields.Binary(string="File", required=True)
    fname = fields.Char(string='Filename')

    def _default_meal_bill_id(self):
        meal_bill_id = self.env['hr.meal.bill'].browse(self.env.context.get(
            'active_id'))
        return meal_bill_id

    meal_bill_id = fields.Many2one(
        'hr.meal.bill',
        default=lambda self: self._default_meal_bill_id(),
        string='Meal Bill',
        required=True
    )

    def _default_description(self):
        meal_bill_id = self.env['hr.meal.bill'].browse(self.env.context.get(
            'active_id'))
        return meal_bill_id.name

    name = fields.Char(string="Description", default=lambda self: self._default_description(), readonly=True)

    def _default_company(self):
        meal_bill_id = self.env['hr.meal.bill'].browse(self.env.context.get(
            'active_id'))
        return meal_bill_id.company_id.id

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self._default_company(),
                                 readonly=True)

    def _default_operating_unit(self):
        meal_bill_id = self.env['hr.meal.bill'].browse(self.env.context.get(
            'active_id'))
        return meal_bill_id.operating_unit_id.id

    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        default=lambda self: self._default_operating_unit(), readonly=True)

    def read_xls_book(self):
        book = xlrd.open_workbook(file_contents=base64.decodestring(self.file))
        sheet = book.sheet_by_index(0)
        # emulate Sheet.get_rows for pre-0.9.4
        values_sheet = []
        for rowx, row in enumerate(map(sheet.row, range(sheet.nrows)), 1):
            if rowx == 1:
                continue
            values = []
            for colx, cell in enumerate(row, 1):
                if cell.ctype in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
                    raise UserError(_("You cannot leave an excel cell empty!"))
                else:
                    if cell.ctype is xlrd.XL_CELL_NUMBER:
                        is_float = cell.value % 1 != 0.0
                        values.append(
                            str(cell.value)
                            if is_float
                            else str(int(cell.value))
                        )
                    elif cell.ctype is xlrd.XL_CELL_DATE:
                        is_datetime = cell.value % 1 != 0.0
                        # emulate xldate_as_datetime for pre-0.9.3
                        dt = datetime.datetime(*xlrd.xldate.xldate_as_tuple(cell.value, book.datemode))
                        values.append(
                            dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                            if is_datetime
                            else dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
                        )
                    elif cell.ctype is xlrd.XL_CELL_BOOLEAN:
                        values.append(u'True' if cell.value else u'False')
                    elif cell.ctype is xlrd.XL_CELL_ERROR:
                        raise ValueError(
                            _("Invalid cell value at row %(row)s, column %(col)s: %(cell_value)s") % {
                                'row': rowx,
                                'col': colx,
                                'cell_value': xlrd.error_text_from_code.get(cell.value,
                                                                            _("unknown error code %s") % cell.value)
                            }
                        )
                    else:
                        values.append(cell.value)
            values_sheet.append(values)
        return values_sheet

    def save_line_data(self, values):
        # ('values', [[u'', '1511', '867'],[u'', '1511', '867']])
        meal_bill_line_obj = self.env['hr.meal.bill.line']
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
                        SELECT id FROM hr_meal_bill_line
                                WHERE employee_id=%s 
                                        AND parent_id=%s
                                    ''' % (employee_obj.id, self.meal_bill_id.id))

                results = self._cr.fetchall()
                if results:
                    for record in results:
                        # checking already uploaded employee
                        if record:
                            errors.append(
                                'AC NO : ' + str(int(val[1])) + ', Error : Employee already uploaded!')
                        else:
                            meal_bill_line_obj.create({
                                'bill_amount': int(val[2]),
                                'parent_id': self.meal_bill_id.id,
                                'employee_id': employee_obj.id,
                                'operating_unit_id': self.operating_unit_id.id,
                                'company_id': self.company_id.id,
                                'device_employee_acc': int(val[1]),
                                'state': 'draft'
                            })

                else:
                    meal_bill_line_obj.create({
                        'bill_amount': int(val[2]),
                        'parent_id': self.meal_bill_id.id,
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
    def meal_bills_import(self):
        if self and self.file:
            try:
                values = []
                values = self.read_xls_book()
                vals = {
                    'meal_bill_id': self.meal_bill_id.id,
                }
                if self.save_line_data(values):
                    message_id = self.env['meal.success.wizard'].create({'message': _(
                        "Meal Bills Created Successfully!")
                    })
                    return {
                        'name': _('Success'),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'meal.success.wizard',
                        'context': vals,
                        'res_id': message_id.id,
                        'target': 'new'
                    }
                else:
                    message_id = self.env['meal.success.wizard'].create({'message': _(
                        "Meal Bills Creation Failed!")
                    })
                    return {
                        'name': _('Failure'),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'meal.success.wizard',
                        'context': vals,
                        'res_id': message_id.id,
                        'target': 'new'
                    }

            except Exception as e:
                raise UserError(_("Meal Bills Uploading Failed!" + ustr(e)))
