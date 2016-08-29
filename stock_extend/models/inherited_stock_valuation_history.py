from openerp import api, fields, models
from openerp.osv import osv


class InheritedWizardValuationHistory(models.Model):
    _inherit = 'wizard.valuation.history'

    choose_category = fields.Boolean(string='Choose a Particular Category')
    product_cat_id = fields.Many2one('product.category', string='Product Category', store=True)

    @api.multi
    def open_category_table(self):
        data = self.read()
        catagory = data[0]['product_cat_id']
        if catagory !=0:
            cat_id = int(data[0]['product_cat_id'][0])
            cat_name = data[0]['product_cat_id'][1]
            date = data[0]['date']

            return {
                'domain': [('product_categ_id', '=', cat_id),('date', '<=', date)],
                'name': cat_name,
                'view_type': 'form',
                'view_mode': 'tree,graph',
                'res_model': 'stock.history',
                'type': 'ir.actions.act_window',
            }
        else:
            raise osv.except_osv(('Warning'), ('enter the category'))
