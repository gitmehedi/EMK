from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import xlrd
import csv
import base64
from datetime import datetime
from odoo.tools import ustr
from collections import OrderedDict

class GbsReadExcelUtility(models.TransientModel):
    _name = 'gbs.read.excel.utility'


    def read_xls_book(self, file):
        book = xlrd.open_workbook(file_contents=base64.decodestring(file))
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
