# -*- coding: utf-8 -*-
from odoo import http

# class GbsPurchaseOrder(http.Controller):
#     @http.route('/gbs_purchase_order/gbs_purchase_order/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/gbs_purchase_order/gbs_purchase_order/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('gbs_purchase_order.listing', {
#             'root': '/gbs_purchase_order/gbs_purchase_order',
#             'objects': http.request.env['gbs_purchase_order.gbs_purchase_order'].search([]),
#         })

#     @http.route('/gbs_purchase_order/gbs_purchase_order/objects/<model("gbs_purchase_order.gbs_purchase_order"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('gbs_purchase_order.object', {
#             'object': obj
#         })