# -*- coding: utf-8 -*-
from odoo import http

# class StockLoanAnalysisReport(http.Controller):
#     @http.route('/stock_loan_analysis_report/stock_loan_analysis_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_loan_analysis_report/stock_loan_analysis_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_loan_analysis_report.listing', {
#             'root': '/stock_loan_analysis_report/stock_loan_analysis_report',
#             'objects': http.request.env['stock_loan_analysis_report.stock_loan_analysis_report'].search([]),
#         })

#     @http.route('/stock_loan_analysis_report/stock_loan_analysis_report/objects/<model("stock_loan_analysis_report.stock_loan_analysis_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_loan_analysis_report.object', {
#             'object': obj
#         })