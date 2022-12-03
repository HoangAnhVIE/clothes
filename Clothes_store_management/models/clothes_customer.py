from odoo import api, fields, models,_
from odoo.exceptions import ValidationError


class ClothesCustomer(models.Model):
    _name = 'clothes.customer'
    _inherit = 'clothes.member'
    _description = 'Clothes Customer'

    bill_ids = fields.One2many('clothes.bill', 'customer_id', string='List Bills', compute='_compute_bill')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env['res.currency']. search([('name', '=', 'USD')]).id, readonly=True)
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    total_bill_paid = fields.Monetary(string='Total Bill Paid', currency_field='currency_id', compute='_compute_total_bill_paid')
    total_bill_unpaid = fields.Monetary(string="Total Bill Unpaid", currency_field='currency_id', compute='_compute_total_bill_unpaid')

    @api.depends('user_id','date_from','date_to')
    def _compute_bill(self):
        for rec in self:
            rec.bill_ids = self.env['clothes.bill'].search([('customer_id', '=', rec.user_id.name), ('book_date', '>=', rec.date_from), ('book_date', '<=', rec.date_to), ])

    @api.depends("bill_ids.total_bill")
    def _compute_total_bill_unpaid(self):
        for rec in self:
            rec.total_bill_unpaid = sum(rec.total_bill for rec in rec.bill_ids.filtered(lambda x: x.state == 'unpaid'))

    @api.depends("bill_ids.total_bill")
    def _compute_total_bill_paid(self):
        for rec in self:
            rec.total_bill_paid = sum(rec.total_bill for rec in rec.bill_ids.filtered(lambda x: x.state == 'paid'))

    _sql_constraints = [
        ('unique_tag_name', 'unique (user_id)', 'Name must be unique')
    ]

    def action_view_customer(self):
        if self.env.user.has_group('Clothes_store_management.group_customer'):
            res_id = self.search([('user_id', '=', self.env.uid)], limit=1).id
            views = [[False, "form"]]
        else:
            views = [[False, "tree"], [False, "form"]]
            res_id = self.search([]).id
        return {
            "type": "ir.actions.act_window",
            "res_model": "clothes.customer",
            "views": views,
            "res_id": res_id,
        }