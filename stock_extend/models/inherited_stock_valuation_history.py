from openerp import api, fields, models
from openerp.osv import osv


class InheritedWizardValuationHistory(models.Model):
    _inherit = 'wizard.valuation.history'

    choose_category = fields.Boolean(string='Choose a Particular Category')
    product_cat_id = fields.Many2one('product.category', string='Product Category', store=True)

    # Searching the sub category
    @api.multi
    def findSubCategory(self, category_ids):
        # category = self.product_cat_id
        categories = self.env['product.category'].browse(category_ids)
        result = []
        for category in categories:
            result.append(category)

        return result

    @api.multi
    def open_category_table(self):
        data = self.read()
        catagory = data[0]['product_cat_id']
        category_ids = self.product_cat_id.child_id.ids

        sub_categories = self.findSubCategory(category_ids)

        if catagory != False and catagory[0] !=0 and sub_categories.__len__() == 0:

            cat_id = int(data[0]['product_cat_id'][0])
            choose_category = data[0]['choose_category']
            cat_name = data[0]['product_cat_id'][1]
            date = data[0]['date']

            return {
                'domain': ['|', '&', ('product_categ_id', '=', cat_id), ('date', '<=', date),
                           ('product_categ_id', '=', cat_id)],
                #  'domain': ['|',('product_categ_id', '=', cat_id),('product_categ_id', '=', catagory[0])],
                'name': cat_name,
                'view_type': 'form',
                'view_mode': 'tree,graph',
                'res_model': 'stock.history',
                'type': 'ir.actions.act_window',
                # 'context': ctx,
            }

        elif sub_categories.__len__() != 0:
            return {
                'domain': [('product_categ_id', 'in', category_ids)],
                # 'name': cat_name,
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
