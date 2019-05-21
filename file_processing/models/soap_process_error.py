# -*- coding: utf-8 -*-

from odoo import exceptions, models, fields, api, _, tools


class ServerFileError(models.Model):
    _name = 'soap.process.error'
    _description = "SOAP Processing Error"
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _order = 'id desc'

    name = fields.Char(string='Title', required=True)
    process_date = fields.Datetime(default=fields.Datetime.now, required=True, readonly=True)
    status = fields.Boolean(default=False, string='Status')
    errors = fields.Text(string='Error Details', required=True)
    state = fields.Selection([('issued', 'Issued'), ('resolved', 'Resolved')], default='issued')

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'issued')]
