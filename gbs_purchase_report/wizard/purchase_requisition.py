from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class PurchaseRequisitionWizard(models.TransientModel):
    _name = 'purchase.requisition.wizard'

    pr_no = fields.Char(string='Purchase Req. No.')
    date_from = fields.Date("Date From", required=True)
    date_to = fields.Date("Date To", required=True)
    type = fields.Selection([('all', 'All'), ('local', 'Local'), ('foreign', 'Foreign')], string='Type', default='all')
    operating_unit_ids = fields.Many2many('operating.unit', string='Operating Unit', default=lambda self: self.env.user.default_operating_unit_id)
    is_only_pending = fields.Boolean(string='Only Pending')

    @api.constrains('date_from', 'date_to')
    def _check_date_validation(self):
        if self.date_from > self.date_to:
            raise ValidationError(_("From date must be less then To date."))
        elif (datetime.strptime(self.date_to, '%Y-%m-%d') - datetime.strptime(self.date_from, '%Y-%m-%d')).days > 365:
            raise ValidationError(_("Maximum date range is one year."))

    @api.onchange('operating_unit_ids')
    def _onchange_operating_unit_ids(self):
        return {'domain': {'operating_unit_ids': [('id', 'in', self.env.user.operating_unit_ids.ids)]}}

    @api.multi
    def get_operating_unit_name(self):
        name = ''
        for rec in self.operating_unit_ids:
            name += rec.name + ', '
        return name[:-2]

    @api.multi
    def process_print(self):
        data = dict()
        data['pr_no'] = self.pr_no
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to
        data['type'] = self.type
        data['operating_unit_ids'] = "(" + str(self.operating_unit_ids.ids[0]) + ")" if len(self.operating_unit_ids.ids) ==1 else str(tuple(self.operating_unit_ids.ids))
        data['operating_unit_name'] = self.get_operating_unit_name()
        data['is_only_pending'] = self.is_only_pending

        return self.env['report'].get_action(self, 'gbs_purchase_report.report_purchase_requisition', data=data)