# -*- coding: utf-8 -*-
from odoo import models, fields, api


class InheritStockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_transfer(self):
        for record in self.move_lines:
            if record.location_dest_id.name == 'Stock':
                self._set_cost_price(record)

        return super(InheritStockPicking, self).do_transfer()

    @api.multi
    def _set_cost_price(self,record):
        cost_price_history = self.env['product.cost.price.history']
        if record.product_id.standard_price > 0:
            current_price = record.product_id.standard_price
        else:
            current_price = record.price_unit
        cost_price_history.create({
            'product_id': record.product_id.id,
            'product_tmpl_id': record.product_id.product_tmpl_id.id,
            'uom_id': record.product_id.uom_id.id,
            'company_id': record.company_id.id,
            'modified_datetime': self.date_done,
            'current_price': round(current_price, 2),
            'old_price': round(self.get_last_price_history(record,self.date_done).current_price, 2) or 0.0,
        })
        if record.product_id.cost_method == 'average':
            update_price_objs = cost_price_history.search([('product_id', '=', record.product_id.id),
                                                           ('modified_datetime', '>', self.date_done)],
                                                          order='modified_datetime ASC')
            if update_price_objs:
                for price_obj in update_price_objs:
                    product_tot_qty_available= 0
                    last_moves = self.env['stock.move'].search([('product_id','=',price_obj.product_id.id),
                                                                ('date','<=',price_obj.modified_datetime),
                                                                ('location_dest_id','=',record.location_dest_id.id),
                                                                ('state' ,'=','done')],
                                                               order='date DESC')
                    if last_moves:
                        for i in last_moves:
                            product_tot_qty_available += i.product_qty

                        amount_unit = self.get_last_price_history(price_obj,price_obj.modified_datetime).current_price or 0.0

                        std_price = ((amount_unit * product_tot_qty_available) + (last_moves[-1].price_unit * last_moves[-1].product_qty)) / (product_tot_qty_available + last_moves[-1].product_qty)
                        price_obj.write({
                            'current_price': round(std_price, 2),
                            'old_price': round(self.get_last_price_history(price_obj,price_obj.modified_datetime).current_price, 2),
                        })
                        record.product_id.with_context(force_company=record.company_id.id).sudo().write(
                            {'standard_price': std_price})


    def get_last_price_history(self,record, date_done):
        if date_done:
            cost_price_history = self.env['product.cost.price.history']
            last_price_objs = cost_price_history.search(
                [('product_id', '=', record.product_id.id), ('modified_datetime', '<', date_done)],
                order='modified_datetime DESC', limit=1)

            return last_price_objs
