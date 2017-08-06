from odoo import api,models,fields
from datetime import datetime

class CustomerCreditLimit(models.AbstractModel):
    _name = "report.gbs_sales_customer_credit_limit.report_credit_limit"
