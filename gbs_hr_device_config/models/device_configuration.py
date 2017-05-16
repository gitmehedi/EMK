from openerp import models, fields
from openerp import api


class DeviceConfiguration(models.Model):
    _name = 'hr.attendance.device.config'

    name = fields.Char(size=100, string='Name', required='True')
    is_active = fields.Boolean(string='Is Active', default=False)
    connection_type = fields.Selection([
        ('url', "URL"),
        ('ip', "IP"),
        ('port', "Port")
    ], string='Connection Type', required=True)
    url = fields.Char(size=100, string='URL')

    device_type = fields.Selection([
        ('primary', "Primary"),
        ('secondary', "Secondary")
    ], string='Device Type', required=True)
    device_id = fields.Integer(string='Device ID', required=True)


    @api.multi
    def toggle_connect(self):
        self.is_active = not self.is_active