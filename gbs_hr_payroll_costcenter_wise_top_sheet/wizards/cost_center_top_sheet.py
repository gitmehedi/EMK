from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from collections import OrderedDict
import operator, math, locale
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import pandas.util.testing as tm
import base64
from pandas import DataFrame


class CostCenterTopSheet(models.TransientModel):
    _name = 'cost.center.top.sheet.wizard'
    _description = 'Cost Center Wise Top Sheet'

    @api.multi
    def _get_payslip_run(self):
        for rec in self:
            rec.hr_payslip_run_id = self.env['hr.payslip.run'].browse(self._context.get('active_id'))

    cost_center_ids = fields.Many2many('account.cost.center', string='Cost Center')
    hr_payslip_run_id = fields.Many2one('hr.payslip.run', compute='_get_payslip_run')

    @api.multi
    def button_export_xlsx(self):
        self.hr_payslip_run_id = self.env['hr.payslip.run'].browse(self._context.get('active_id'))
        return self.env['report'].get_action(self,
                                             report_name='gbs_hr_payroll_costcenter_wise_top_sheet.cost_center_wise_top_sheet_xlsx')

    @api.multi
    def button_export_xlsx_pandas(self):
        self.hr_payslip_run_id = self.env['hr.payslip.run'].browse(self._context.get('active_id'))
        top_sheet = self.hr_payslip_run_id

        header = OrderedDict()
        # if header_created == 0:
        header[0] = 'Cost Center'
        header[1] = 'Department'
        header[2] = 'Employee'
        # for rec in final_rule_list:
        #     header[len(header)] = rec[1]
        header_list = []
        for key, value in header.items():
            header_list.append(value)
        writer = pd.ExcelWriter('/tmp/' + top_sheet.name + '.xls', engine='xlsxwriter')

        df = DataFrame(None, columns=header_list)

        writer.save()
        PREVIEW_PATH = '/tmp/' + top_sheet.name + '.xls'
        encoded_string = ""
        with open(PREVIEW_PATH, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
    # self.file_name = '/tmp/'+top_sheet+'.xls'
    # self.file_output = encoded_string
