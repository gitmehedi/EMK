from odoo import api, fields, models,_

class AppLetter(models.Model):
    _name ='app.letter'
    _description= 'Appointment Letter'

    name = fields.Char('Name', required=True)