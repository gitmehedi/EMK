from openerp import models, fields
from openerp import api
import json


class DeviceLine(models.Model):
    _name = 'hr.attendance.device.line'

    name = fields.Char(size=100, string='Name', required='True')
    sensor_id = fields.Char(string='Machine Number', size=5, required=True)
    # in_code = fields.Char(string='In Code', size=5, required=True, default='1')
    # out_code = fields.Char(string='Out Code', size=5, required=True, default='101')


    """" Relational Fields """
    device_detail_id = fields.Many2one("hr.attendance.device.detail", string="Device Details", required=True, ondelete='cascade')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'This Name is already in use'),
        ('sensor_id_uniq', 'unique(sensor_id)', 'This Device ID is already in use'),
    ]

