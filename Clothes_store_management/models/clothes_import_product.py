from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError


class ClothesImportProduct(models.Model):
    _name = 'clothes.import.product'
    _description = 'Clothes Import Product'
    _rec_name = 'warehouse_id'

    supplier_id = fields.Many2one('clothes.supplier', string="Suppliers")
    warehouse_id = fields.Many2one('clothes.warehouse', string="Warehouse")
    product_code = fields.Char(string='Product', compute= '_compute_product_code')
    date_import = fields.Datetime(string="Date import", default=datetime.today())
    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')]).id,readonly=True)
    import_price = fields.Monetary(string='Import price', currency_field='currency_id')
    import_quantity = fields.Integer(string="Import quantity")
    total_amount_import = fields.Monetary(string="Total amount import", compute="_compute_total_amount_import")

    @api.depends('import_price', 'import_quantity')
    def _compute_total_amount_import(self):
        for rec in self:
            if rec.import_price and rec.import_quantity:
                rec.total_amount_import = rec.import_price * rec.import_quantity
            else:
                rec.total_amount_import = 0

    @api.depends('warehouse_id.product_id')
    def _compute_product_code(self):
        for rec in self:
            rec.product_code = rec.warehouse_id.product_id.product_code