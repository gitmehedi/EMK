from odoo import fields, models, api

class IndentType(models.Model):
    _name = "indent.type"
    _description = "Indent Type"
    _order = "id"

    name = fields.Char('Type Name')