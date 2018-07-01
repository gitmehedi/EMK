from odoo import api, fields, models

class ProductTemplate(models.Model):
    
    _inherit = 'product.template'
    
    report_type = fields.Selection([("rm", "Raw Materials"),
                                    ("cons", "Consumable"),
                                    ("pack", "Packaging"),
                                    ("mach", "Machines"),
                                    ("chem", "Chemicals"),
                                    ("pain", "Painting"),
                                    ("access", "Accessories"),
                                    ("spare", "Spare Parts"),
                                    ("fg", "Finished Goods"),
                                    ("sfg", "Semi Finished Goods"),],
                                   string='Report Type')
