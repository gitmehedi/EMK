from odoo import api, fields, models, _

class DocumentType(models.Model):
    _name = "document.type"

    name = fields.Char("Document Name", required=True)
    sequence = fields.Integer("Sequence")
    active = fields.Boolean("Active")