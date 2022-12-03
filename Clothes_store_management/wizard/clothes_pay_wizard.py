from odoo import api, fields, models, _
from datetime import datetime


class ClothesPayWizard(models.TransientModel):
    _name = 'clothes.pay.wizard'
    _description = 'Create new pay'

    bill_id = fields.Many2one(
        string="Bill",
        comodel_name='clothes.bill',
        readonly=True,
        default=lambda self: self.env.context.get('active_id'),
    )
    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')]).id, readonly=True)
    total_bill = fields.Monetary(string="Total money", currency_field='currency_id',related ='bill_id.total_bill' )
    type_pay = fields.Selection([('cash', 'Cash'), ('bank', 'Bank')], default ='bank' , string="Type Pay")
    pay_date = fields.Datetime(string="Pay Date", default=datetime.today())
    pay_money = fields.Monetary(string="Pay money",currency_field='currency_id')
    excess_cash = fields.Monetary(string='Excess cash',currency_field='currency_id', compute='_compute_excess_cash')

    @api.depends('total_bill', 'pay_money')
    def _compute_excess_cash(self):
        for rec in self:
            if rec.pay_money and rec.total_bill:
                rec.excess_cash = rec.pay_money - rec.total_bill
            else:
                rec.excess_cash = 0

    def pay(self):
        for rec in self:
            rec.bill_id.state = 'paid'