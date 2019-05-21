# -*- coding: utf-8 -*-

from odoo import exceptions, models, fields, api, _, tools


class ServerFileError(models.Model):
    _name = 'server.file.error'
    _description = "File Processing Error"
    _inherit = ["mail.thread"]
    _order = 'id desc'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    process_date = fields.Datetime(default=fields.Datetime.now)
    file_path = fields.Char(string='File Path')
    ftp_ip = fields.Char(string='FTP IP')
    status = fields.Boolean(default=False, string='Status')
    errors = fields.Text(string='Error Details')
    state = fields.Selection([('issued', 'Issued'), ('resolved', 'Resolved')], default='issued')

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'issued')]

    @api.depends('file_path', 'ftp_ip')
    def _compute_name(self):
        for rec in self:
            rec.name = "{0} and {1}".format(rec.ftp_ip, rec.file_path)
