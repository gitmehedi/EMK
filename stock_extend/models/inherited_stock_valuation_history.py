from openerp import api, fields, models
from openerp.osv import osv
from openerp import tools
from openerp.tools.translate import _


class InheritedWizardValuationHistory(models.Model):
    _inherit = 'wizard.valuation.history'

    choose_category = fields.Boolean(string='Choose a Particular Category')
    product_cat_id = fields.Many2one('product.category', string='Product Category', store=True)

    # Searching the sub category
    @api.multi
    def find_sub_category(self, category_ids):
        # category = self.product_cat_id
        categories = self.env['product.category'].browse(category_ids)
        result = []
        for category in categories:
            result.append(category)

        return result

    @api.multi
    def open_category_table(self):
        data = self.read()
        category = self.product_cat_id

        cat_pool = self.env['product.category']
        categories = cat_pool.get_categories(category.id)

        if category != False and self.date:
            return {
                'domain': [('product_categ_id', 'in', categories), ('date', '<=', self.date)],
                'name': category.name,
                'view_type': 'form',
                'view_mode': 'tree,graph',
                'res_model': 'stock.history',
                'type': 'ir.actions.act_window',
                # 'context': ctx,
            }
        elif category != False:
            return {
                'domain': [('product_categ_id', 'in', categories)],
                'name': category.name,
                'view_type': 'form',
                'view_mode': 'tree,graph',
                'res_model': 'stock.history',
                'type': 'ir.actions.act_window',
                # 'context': ctx,
            }
        else:
            raise osv.except_osv(('Warning'), ('Select Category !'))


class InheritedStockHistory(models.Model):
    _inherit = 'stock.history'
    
    uom = fields.Many2one('product.uom', string="UOM", related='product_id.uom_id')
    
    

