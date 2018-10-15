from odoo import api, fields, models


class InheritedProductProduct(models.Model):
    _inherit = 'sale.order.line'


    @api.multi
    def _prepare_invoice_line(self, qty):

        res = super(InheritedProductProduct, self)._prepare_invoice_line(qty=qty)

        #---------------------------------------------
        # Business:
        # 1. Local + LC + USD = Deemed Export
        # 2. Local + LC + BDT = Local LC
        # 3. Foreign + LC + USD/BDT = Foreign Export
        # 4. Cash sales = Cash Sales
        #---------------------------------------------

        if len(self.product_id.product_income_acc) > 0:
            for prod_income in self.product_id.product_income_acc:


                if not prod_income.so_type_id.sale_order_type or not prod_income.sale_local_foreign or not prod_income.currency_id:
                    return res

                if prod_income.so_type_id.sale_order_type == 'lc_sales' \
                        and prod_income.sale_local_foreign == 'local':

                        if prod_income.currency_id.name == 'USD':
                            res['account_id'] = prod_income.account_id.id
                            break;

                        elif self.product_id.currency_id.name == 'BDT':
                            res['account_id'] = prod_income.account_id.id
                            break;

                elif prod_income.so_type_id.sale_order_type == 'lc_sales' \
                        and prod_income.sale_local_foreign == 'foreign' \
                        and (prod_income.currency_id.name == 'BDT' or prod_income.currency_id.name == 'USD'):

                        res['account_id'] = prod_income.account_id.id
                        break;

                elif prod_income.so_type_id.sale_order_type == 'cash_sales':
                        res['account_id'] = prod_income.account_id.id
                        break;

        return res

