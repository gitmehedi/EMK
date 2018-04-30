from odoo import tools
from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class StockLoanLendingReport(models.Model):
    _name = 'stock.loan.lending.report'
    _description = "Stock Loan Lending Statistics"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    loan_no = fields.Char(string='Stock Loan No.', readonly=True)
    date = fields.Datetime(string='Request Date', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_uom_qty = fields.Float(string='Quantity',readonly=True,digits=dp.get_precision('Product UoS'),)
    product_specification = fields.Text(string='Specification', readonly=True)
    borrower_id = fields.Many2one('res.partner', string="Request By", readonly=True)
    issuer_id = fields.Many2one('res.users', string='Issue By', readonly=True,)
    approver_id = fields.Many2one('res.users', string='Authority', readonly=True)
    company_id = fields.Many2one('res.company',string='Company', readonly=True)
    operating_unit_id = fields.Many2one('operating.unit',string= 'Operating Unit', readonly=True)
    approved_date = fields.Datetime(string='Approved Date',readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('reject', 'Rejected'),
    ], string='State', readonly=True)

    def _select(self):
        select_str = """
        SELECT  l.id,
                i.name as loan_no, 
                i.request_date as date,
                i.issuer_id,
                i.approved_date, 
                i.approver_id, 
                i.company_id, 
                i.operating_unit_id,  
                l.product_id, 
                l.product_uom_qty, 
                l.name as product_specification, 
                i.borrower_id, 
                i.state
        """
        return select_str

    def _from(self):
        from_str = """
            item_loan_lending_line l 
            join item_loan_lending i on (l.item_loan_lending_id=i.id)
        """
        return from_str


    @api.model_cr
    def init(self):
        # self._table = stock_loan_lending_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
                %s
                FROM ( %s )
                )""" % (self._table, self._select(), self._from()))





class StockLoanBorrowingReport(models.Model):
    _name = 'stock.loan.borrowing.report'