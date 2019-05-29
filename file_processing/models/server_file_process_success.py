# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ServerFileSuccess(models.Model):
    _name = 'server.file.success'
    _description = "GLIF File Success"
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _order = 'id desc'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    start_date = fields.Datetime(string='Start Datetime', required=True)
    stop_date = fields.Datetime(string='Stop Datetime', required=True)
    file_name = fields.Char(string='File Path', required=True)
    upload_file = fields.Binary(string="Upload File", attachment=True)
    status = fields.Boolean(default=False, string='Status')
