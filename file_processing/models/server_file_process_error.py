# -*- coding: utf-8 -*-

from odoo import exceptions, models, fields, api, _, tools


class ServerFileError(models.Model):
    _name = 'server.file.error'
    _description = "File Processing Error"
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _order = 'id desc'

    name = fields.Char(string='Name')
    process_date = fields.Datetime(default=fields.Datetime.now)
    file_path = fields.Char(string='File Path')
    ftp_ip = fields.Char(string='FTP IP')
    status = fields.Boolean(default=False, string='Status')
    errors = fields.Text(string='Error Details')
    state = fields.Selection([('issued', 'Issued'), ('resolved', 'Resolved')], default='issued')
    line_ids = fields.One2many('server.file.error.line', 'line_id', readonly=True)

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'issued')]

    @api.depends('file_path', 'ftp_ip')
    def _compute_name(self):
        for rec in self:
            if rec.file_path and rec.ftp_ip:
                rec.name = "{0} and {1}".format(rec.ftp_ip, rec.file_path)


class ServerFileErrorDetails(models.Model):
    _name = 'server.file.error.line'
    _description = "File Processing Error Details"
    _inherit = ["mail.thread"]
    _order = 'id asc'

    process_date = fields.Datetime(default=fields.Datetime.now)
    line_no = fields.Char(string='Line No')
    status = fields.Boolean(default=False, string='Status')
    details = fields.Text(string='Error Details')
    line_id = fields.Many2one('server.file.error')
