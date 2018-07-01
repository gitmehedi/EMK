from odoo import tools
from odoo import models, fields, api

class StockLoanLendingReport(models.Model):
    _name = 'stock.loan.lending.report'
    _description = "Stock Loan Lending Statistics"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    loan_no = fields.Char(string='Stock Loan No.', readonly=True)
    date = fields.Datetime(string='Request Date', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_uom_qty = fields.Float(string='Issued Quantity',readonly=True)
    received_qty = fields.Float('Received Quantity', readonly=True)
    given_qty = fields.Float('Given Quantity', readonly=True)
    due = fields.Float('Due', readonly=True)
    product_uom = fields.Many2one('product.uom', 'Unit of Measure', readonly=True)
    categ_id = fields.Many2one('product.category', 'Product Category', readonly=True)
    product_specification = fields.Text(string='Specification', readonly=True)
    borrower_id = fields.Many2one('res.partner', string="Requested Company", readonly=True)
    issuer_id = fields.Many2one('res.users', string='Issue By', readonly=True,)
    approver_id = fields.Many2one('res.users', string='Approver', readonly=True)
    company_id = fields.Many2one('res.company',string='Company', readonly=True)
    operating_unit_id = fields.Many2one('operating.unit',string= 'Operating Unit', readonly=True)
    approved_date = fields.Datetime(string='Approved Date',readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('received', 'Received'),
        ('reject', 'Rejected'),
    ], string='State', readonly=True)

    def _select(self):
        select_str = """
        SELECT  min(l.id) as id,
                l.product_id,
                l.name as product_specification,
                t.uom_id as product_uom,
                t.categ_id as categ_id,
                sum(l.product_uom_qty) as product_uom_qty,
                sum(l.received_qty) as received_qty,
                sum(l.given_qty) as given_qty,
                sum(l.given_qty) - sum(l.received_qty) as due,
                i.name as loan_no, 
                i.request_date as date,
                i.issuer_id,
                i.approved_date, 
                i.approver_id, 
                i.borrower_id, 
                i.company_id, 
                i.operating_unit_id,
                i.state
        """
        return select_str

    def _from(self):
        from_str = """
            item_loan_lending_line l 
            join item_loan_lending i on (l.item_loan_lending_id=i.id)
            left join product_product p on (l.product_id=p.id)
            left join product_template t on (p.product_tmpl_id=t.id)
            left join product_uom u on (u.id=l.product_uom)
            left join product_uom u2 on (u2.id=t.uom_id)
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY l.product_id,
                    l.name,
                    t.uom_id,
                    t.categ_id,
                    i.name,
                    i.request_date,
                    i.issuer_id,
                    i.approved_date,
                    i.approver_id,
                    i.borrower_id,
                    i.company_id,
                    i.operating_unit_id,
                    i.state
        """
        return group_by_str

    @api.model_cr
    def init(self):
        # self._table = stock_loan_lending_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
                    %s
                    FROM ( %s )
                    %s
                    )""" % (self._table, self._select(), self._from(), self._group_by()))



class StockLoanBorrowingReport(models.Model):
    _name = 'stock.loan.borrowing.report'
    _description = "Stock Loan Borrowing Statistics"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    loan_no = fields.Char(string='Stock Loan No.', readonly=True)
    date = fields.Datetime(string='Request Date', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_uom_qty = fields.Float(string='Issued Quantity', readonly=True)
    received_qty = fields.Float('Received Quantity',readonly=True)
    given_qty = fields.Float('Given Quantity', readonly=True)
    due = fields.Float('Due', readonly=True)
    product_uom = fields.Many2one('product.uom', 'Unit of Measure', readonly=True)
    categ_id = fields.Many2one('product.category', 'Product Category', readonly=True)
    product_specification = fields.Text(string='Specification', readonly=True)
    partner_id = fields.Many2one('res.partner', string="Partner Company", readonly=True)
    issuer_id = fields.Many2one('res.users', string='Issue By', readonly=True, )
    approver_id = fields.Many2one('res.users', string='Approver', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', readonly=True)
    approved_date = fields.Datetime(string='Approved Date', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('reject', 'Rejected'),
    ], string='State', readonly=True)

    def _select(self):
        select_str = """
            SELECT  min(l.id) as id,
                    l.product_id,
                    l.name as product_specification,
                    t.uom_id as product_uom,
                    t.categ_id as categ_id,
                    sum(l.product_uom_qty) as product_uom_qty,
                    sum(l.received_qty) as received_qty,
                    sum(l.given_qty) as given_qty,
                    sum(l.received_qty) - sum(l.given_qty) as due,
                    i.name as loan_no, 
                    i.request_date as date,
                    i.issuer_id,
                    i.approved_date, 
                    i.approver_id, 
                    i.partner_id, 
                    i.company_id, 
                    i.operating_unit_id,
                    i.state
            """
        return select_str

    def _from(self):
        from_str = """
                item_borrowing_line l 
                join item_borrowing i on (l.item_borrowing_id=i.id)
                left join product_product p on (l.product_id=p.id)
                left join product_template t on (p.product_tmpl_id=t.id)
                left join product_uom u on (u.id=l.product_uom)
                left join product_uom u2 on (u2.id=t.uom_id)
            """
        return from_str

    def _group_by(self):
        group_by_str = """
                GROUP BY l.product_id,
                        l.name,
                        t.uom_id,
                        t.categ_id,
                        i.name,
                        i.request_date,
                        i.issuer_id,
                        i.approved_date,
                        i.approver_id,
                        i.partner_id,
                        i.company_id,
                        i.operating_unit_id,
                        i.state
            """
        return group_by_str

    @api.model_cr
    def init(self):
        # self._table = stock_loan_borrowing_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
                        %s
                        FROM ( %s )
                        %s
                        )""" % (self._table, self._select(), self._from(), self._group_by()))