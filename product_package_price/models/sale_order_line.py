from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    new_qty = fields.Float(string="New Qty")
    package_price = fields.Float(string="Package Price")
    _package_price_initialized = fields.Boolean(default=False)
    new_qty_last = fields.Float(string="Previous New Qty", default=0.0, store=True)
    delta_qty = fields.Float(string="Delta Qty", compute="_compute_delta_qty", store=False)

    product_packaging_qty = fields.Float(
        string='Packaging Quantity',
        digits=(16, 3),
    )

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        res['package_qty'] = self.product_packaging_qty
        res['pieces_qty'] = self.new_qty or 0.0
        return res

    def _prepare_procurement_values(self, group_id=False):
        values = super()._prepare_procurement_values(group_id)
        self.ensure_one()
        values.update({
            'package_qty': self.product_packaging_qty,
            'pieces_qty': self.new_qty or 0.0
        })
        return values

    @api.onchange('product_id')
    def _onchange_product_id_set_first_packaging(self):
        for line in self:
            if line.product_id and not line.product_packaging_id and line.product_id.packaging_ids:
                line.product_packaging_id = line.product_id.packaging_ids[0]

    @api.onchange('product_packaging_id')
    def _onchange_product_packaging_id(self):
        for line in self:
            if line.product_packaging_id and not line._package_price_initialized:
                line.package_price = line.product_packaging_id.package_sale_price or 0.0
                line._package_price_initialized = True
            line._update_qty_and_prices()

    @api.onchange('product_packaging_qty')
    def _onchange_packaging_qty(self):
        for line in self:
            line._update_qty_and_prices()

    @api.onchange('package_price')
    def _onchange_package_price(self):
        for line in self:
            line._update_qty_and_prices()

    @api.depends('new_qty', 'new_qty_last')
    def _compute_delta_qty(self):
        for line in self:
            line.delta_qty = line.new_qty - line.new_qty_last

    @api.onchange('new_qty')
    def _onchange_new_qty(self):
        for line in self:
            delta = line.new_qty - line.new_qty_last
            line.product_uom_qty += delta
            line._update_qty_and_prices()

    def _update_qty_and_prices(self):
        for line in self:
            pieces_per_box = line.product_packaging_id.qty or 1.0
            boxes = line.product_packaging_qty or 0.0
            extra_pieces = line.new_qty or 0.0

            total_pieces = (boxes * pieces_per_box) + extra_pieces
            line.product_uom_qty = total_pieces
            line.price_unit = line.package_price / pieces_per_box if pieces_per_box else 0.0

    def write(self, vals):
        res = super().write(vals)
        for line in self:
            if 'new_qty' in vals:
                line.new_qty_last = line.new_qty
            line._update_qty_and_prices()
        return res

    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            line.new_qty_last = line.new_qty or 0.0
            line._update_qty_and_prices()
        return lines

    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_id_check_stock(self):
        if self.product_id and self.product_uom_qty:
            qty_available = self.product_id.qty_available
            if self.product_uom_qty > qty_available:
                raise UserError(f"The selected product '{self.product_id.display_name}' is out of stock. Only {qty_available} unit(s) available.")

    @api.constrains('product_id', 'product_uom_qty')
    def _check_product_stock(self):
        for line in self:
            if line.product_id.type == 'product':
                qty_available = line.product_id.qty_available
                if line.product_uom_qty > qty_available:
                    raise ValidationError(
                        f"Cannot confirm order. Product '{line.product_id.display_name}' has only {qty_available} unit(s) in stock."
                    )
