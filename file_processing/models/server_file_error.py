# -*- coding: utf-8 -*-

from odoo import exceptions, models, fields, api, _, tools


class ServerFileError(models.Model):
    _name = 'server.file.error'
    _inherit = ["mail.thread"]

    move_id = fields.Many2one('account.move', string='Account Move')
    process_date = fields.Datetime(default=fields.Datetime.now)
    file_path = fields.Text()
    status = fields.Boolean(default=False, string='Status')
    errors = fields.Text(string='Error Details')
