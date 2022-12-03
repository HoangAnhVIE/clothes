from odoo import api, fields, models
from datetime import date
from odoo.exceptions import ValidationError


class ClothesMember(models.Model):
    _name = 'clothes.member'
    _description = 'Clothes Member'

    user_id = fields.Many2one('res.users', string='User Name', required=True)
    name = fields.Char(string='Name', related='user_id.name')
    phone = fields.Char(string='Phone', related='user_id.phone', readonly=False)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender', default='male')
    email = fields.Char(string="Email", related='user_id.login', readonly=False)
    date_of_birth = fields.Date(string='Date of birth', required=True)
    age = fields.Integer(string='Age', compute="_compute_age")
    address = fields.Char(string='Address')
    image = fields.Binary(string='Avatar', attachment=True, help='Avatar', related='user_id.avatar_1920', store=True,)

    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            today = date.today()
            if rec.date_of_birth:
                rec.age = today.year - rec.date_of_birth.year
            else:
                rec.age = 0

    @api.constrains('date_of_birth')
    def _check_date_of_birth(self):
        for r in self:
            if r.date_of_birth > fields.Date.today():
                raise ValidationError('Date of Birth must be in the past')
