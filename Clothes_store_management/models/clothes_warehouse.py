from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ClothesWarehouse(models.Model):
    _name = 'clothes.warehouse'
    _description = 'Clothes Warehouse'

    name = fields.Char(related = 'product_id.product_code')
    product_id = fields.Many2one('clothes.product', string="Product")
    image = fields.Binary(related='product_id.image')
    import_product_ids = fields.One2many('clothes.import.product', 'warehouse_id', string="Import product")
    bill_details_ids = fields.One2many('clothes.bill.details', 'warehouse_id', string='Bill Details',)
    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')]).id,readonly=True)
    total_import = fields.Integer(string='Total Imported', compute='_compute_total_import')
    export_quantity = fields.Integer(string="Amount Paid",compute='_compute_export_quantity')
    export_quantity_unpaid = fields.Integer(string="Amount Unpaid",compute='_compute_export_quantity_unpaid')
    inventory = fields.Integer(string="Inventory", compute='_compute_inventory')
    turnover = fields.Monetary(string="Turnover", compute='_compute_turnover')
    turnover_unpaid = fields.Monetary(string="Turnover Unpaid", compute="_compute_turnover_unpaid")
    turnover_expected = fields.Monetary(string="Turnover Expected", compute='_compute_turnover_expected')
    total_import_value = fields.Monetary(string='Total import value', currency_field='currency_id', compute='_compute_total_import_value')

    @api.depends('total_import', 'export_quantity','export_quantity_unpaid')
    def _compute_inventory(self):
        for rec in self:
            if rec.total_import and rec.export_quantity and rec.export_quantity_unpaid:
                rec.inventory = rec.total_import - rec.export_quantity - rec.export_quantity_unpaid
            elif rec.total_import and rec.export_quantity_unpaid:
                rec.inventory = rec.total_import - rec.export_quantity_unpaid
            else:
                rec.inventory = rec.total_import - rec.export_quantity

    @api.depends('import_product_ids.import_quantity')
    def _compute_total_import(self):
        total_import = 0
        for rec in self:
            rec.total_import = sum(rec.import_quantity for rec in rec.import_product_ids)

    @api.depends('import_product_ids.total_amount_import')
    def _compute_total_import_value(self):
        total_import_value = 0
        for rec in self:
            rec.total_import_value = sum(rec.total_amount_import for rec in rec.import_product_ids)

    @api.depends('bill_details_ids.quantity')
    def _compute_export_quantity(self):
        for rec in self:
            rec.export_quantity = sum(rec.quantity for rec in rec.product_id.bill_details_ids.filtered(lambda x: x.bill_id.state == 'paid'))

    @api.depends('bill_details_ids.quantity')
    def _compute_export_quantity_unpaid(self):
        for rec in self:
            rec.export_quantity_unpaid = sum(
                rec.quantity for rec in rec.product_id.bill_details_ids.filtered(lambda x: x.bill_id.state == 'unpaid'))

    @api.depends('bill_details_ids.total_bill_details','bill_details_ids.bill_id.state')
    def _compute_turnover(self):
        turnover = 0
        for rec in self:
            rec.turnover = sum(rec.total_bill_details for rec in rec.product_id.bill_details_ids.filtered(lambda x: x.bill_id.state == 'paid'))

    @api.depends('bill_details_ids.total_bill_details', 'bill_details_ids.bill_id.state')
    def _compute_turnover_unpaid(self):
        for rec in self:
            rec.turnover_unpaid = sum(rec.total_bill_details for rec in
                               rec.product_id.bill_details_ids.filtered(lambda x: x.bill_id.state == 'unpaid'))

    @api.depends('bill_details_ids.total_bill_details', 'bill_details_ids.bill_id.state')
    def _compute_turnover_expected(self):
        turnover_expected = 0
        for rec in self:
            rec.turnover_expected = rec.turnover_unpaid + rec.turnover

    @api.onchange('import_product_ids')
    def _onchange_order_quantity(self):
        for rec in self.import_product_ids:
            if rec.import_quantity == 0:
                raise ValidationError('You must enter at least one product! ')

    @api.onchange('product_id')
    def _onchange_duplicate(self):
        len_bill = len(self.product_id)
        for i in range(len_bill - 1):
            if self.product_id[len_bill - 1].product_code == self.product_id[i].product_code:
                raise ValidationError('You have to buy another product')

    @api.onchange('import_product_ids','product_id')
    def _onchange_import_product(self):
        for rec in self.import_product_ids:
            if rec.import_quantity == 0:
                raise ValidationError('You need to import at least 1 product!')

    _sql_constraints = [
        ('unique_tag_name', 'unique (product_id)', 'Name must be unique')
    ]