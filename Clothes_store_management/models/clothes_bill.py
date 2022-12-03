from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError


class ClothesBill(models.Model):
    _name = 'clothes.bill'
    _description = 'Clothes Bill'

    name = fields.Char(string = 'Name', compute='_compute_name')
    bill_details_ids = fields.One2many('clothes.bill.details', 'bill_id', string="Bill Details")
    staff_id = fields.Many2one('clothes.staff', string="Staffs")
    customer_id = fields.Many2one('clothes.customer', string="Customers", required=True)
    pay_ids = fields.One2many('clothes.pay.wizard','bill_id', string='Pay')
    book_date = fields.Datetime(string="Book Date", default=datetime.today())
    pay_date = fields.Datetime(string="Pay Date", default=datetime.today(), compute='_compute_pay_date')
    book_type = fields.Selection([('store', 'Store'), ('ship', 'Ship')], default='ship')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env['res.currency']. search([('name', '=', 'USD')]).id, readonly=True)
    address = fields.Char(related='customer_id.address', readonly=False)
    fee_ship = fields.Monetary(string="Fee Ship", currency_field='currency_id')
    discount_bill = fields.Integer(string='Discount %')
    total_bill = fields.Monetary(string="Total Bill", currency_field='currency_id', compute='_compute_total_bill')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('unpaid', 'Unpaid'), ('paid', 'Paid')], default='draft', string="Status",)

    @api.constrains('bill_details_ids')
    def _check_empty_bill(self):
        if not self.bill_details_ids:
            raise ValidationError('The bill detail is empty!')

    @api.onchange('bill_details_ids')
    def _onchange_bill_detail(self):
        for rec in self.bill_details_ids:
            if rec.quantity > rec.product_id.quantity:
                raise ValidationError('Not enough products')
            elif rec.product_id.quantity <= 0:
                raise ValidationError('You need to import at least 1 product!')
            elif rec.quantity <= 0:
                raise ValidationError('You must order at least one product!')

    @api.onchange('bill_details_ids')
    def _onchange_duplicate(self):
        len_bill = len(self.bill_details_ids)
        for i in range(len_bill - 1):
            if self.bill_details_ids[len_bill - 1].product_id.id == self.bill_details_ids[i].product_id.id:
                raise ValidationError('You have to buy another product')

    @api.depends("bill_details_ids.total_bill_details","discount_bill")
    def _compute_total_bill(self):
        for rec in self:
            if rec.book_type == 'store':
                rec.total_bill = ((100 - rec.discount_bill) / 100) * sum(
                    rec.total_bill_details for rec in rec.bill_details_ids)
            else:
                rec.total_bill = ((100 - rec.discount_bill) / 100) * sum(
                    rec.total_bill_details for rec in rec.bill_details_ids) + rec.fee_ship

    @api.depends('customer_id', 'book_date')
    def _compute_name(self):
        for rec in self:
            if rec.customer_id and rec.book_date:
                rec.name = str(rec.customer_id.name) + " -- " + str(rec.book_date)

    @api.depends('pay_ids.pay_date')
    def _compute_pay_date(self):
        for rec in self:
            rec.pay_date = rec.pay_ids.pay_date

    def action_confirm(self):
        if self.book_type == 'ship':
            self.state = 'confirm'
        else:
            self.state = 'unpaid'

    def action_unpaid(self):
        self.state = 'unpaid'

    def action_cancel(self):
        self.state = 'draft'

    # def unlink(self):
    #     for rec in self:
    #         if rec.state == 'paid':
    #             raise ValidationError(_('You cannot delete paid bills!'))
    #     return super(ClothesBill, self).unlink()
