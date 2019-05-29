# -*- coding: utf-8 -*-

from datetime import datetime as dt
from odoo import models, fields, api, _

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


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
    time = fields.Text(string='Time', compute="_compute_time")
    status = fields.Boolean(default=False, string='Status')

    @api.depends('start_date', 'stop_date')
    def _compute_time(self):
        for rec in self:
            diff = dt.strptime(rec.stop_date, TIME_FORMAT) - dt.strptime(rec.start_date, TIME_FORMAT)
            rec.time = str(diff)