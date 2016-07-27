from openerp import api, exceptions, fields, models

class QuotationSubmission(models.Model):
    _name="quotation.submission"
    
    submission_date = fields.Date(default=fields.Date.today(), string="Submission Date", required=True)
    quotation_request_id = fields.Many2one('quotation.request', string="Quotation Request")
    product_costing_id = fields.Many2one('product.costing', string="Product Costing")
    remarks = fields.Text(string="Remarks")
      
    _sql_constraints = [
        ('_check_date_comparison', "CHECK (quotation_request_id.quotation_request_date <= submission_date)", "The Submission date must be greater than Quotation Request date.")
    ] 