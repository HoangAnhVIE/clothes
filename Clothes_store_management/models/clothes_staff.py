from odoo import api, fields, models
from datetime import date
from odoo.exceptions import ValidationError


class ClothesStaff(models.Model):
    _name = 'clothes.staff'
    _inherit = 'clothes.member'
    _description = 'Clothes Staff'

    bill_ids = fields.One2many('clothes.bill', 'staff_id', string='Bills',compute='_compute_bill')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')]).id,
                                  readonly=True)
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    total_bill_paid = fields.Monetary(string='Total Bill Paid', currency_field='currency_id',
                                      compute='_compute_total_bill_paid')

    @api.depends("bill_ids.total_bill")
    def _compute_total_bill_paid(self):
        for rec in self:
            rec.total_bill_paid = sum(rec.total_bill for rec in rec.bill_ids.filtered(lambda x: x.state == 'paid'))

    @api.depends('user_id', 'date_from', 'date_to')
    def _compute_bill(self):
        for rec in self:
            rec.bill_ids = self.env['clothes.bill'].search(
                [('staff_id', '=', rec.user_id.name), ('pay_date', '>=', rec.date_from),
                 ('pay_date', '<=', rec.date_to),('state','=', 'paid')])

    _sql_constraints = [
        ('unique_tag_name', 'unique (user_id)', 'Name must be unique')
    ]

    @api.constrains('date_of_birth')
    def _check_date_of_birth(self):
        for rec in self:
            today = date.today()
            if today.year - rec.date_of_birth.year < 18:
                raise ValidationError('Age staff need >= 18')