from odoo import api, fields, models


class SuccessMsg(models.TransientModel):
    _name = 'success.msg.wizard'