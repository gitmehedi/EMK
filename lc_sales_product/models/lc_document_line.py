from odoo import api, fields, models, _

class LcDocumentLine(models.Model):
    _name = "lc.document.line"

    doc_name = fields.Many2one("document.type", required=True)
    original = fields.Char("Original", required=True)
    copy = fields.Integer("Copys", required=True)
    lc_id = fields.Many2one('letter.credit')