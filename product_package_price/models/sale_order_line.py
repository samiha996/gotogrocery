

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    
    package_price = fields.Float(string="Package Price")
    _package_price_initialized = fields.Boolean(default=False)

    second_product_uom_qty = fields.Float()

    product_packaging_qty = fields.Float(
        string="Packaging Quantity",
        compute=False,
        store=True, readonly=False, precompute=True)

    product_uom_qty = fields.Float(
        string="Quantity",
        compute='_compute_product_uom_qty',
        digits='Product Unit of Measure', default=False,
        store=True, readonly=False, required=True, precompute=True)
    
    price_unit = fields.Float(
        string='Unit Price',
        compute='_update_price',
        digits='Product Price', default=0.0,
        store=True, readonly=False, precompute=True)

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        res['package_qty'] = self.product_packaging_qty
        res['pieces_qty'] = self.second_product_uom_qty or 0.0
        return res

    def _prepare_procurement_values(self, group_id=False):
        values = super()._prepare_procurement_values(group_id)
        self.ensure_one()
        values.update({
            'package_qty': self.product_packaging_qty,
            'pieces_qty': self.second_product_uom_qty or 0.0
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
            if line.product_packaging_id:
                if not line._package_price_initialized:
                    line.package_price = line.product_packaging_id.package_sale_price or 0.0
                    line._package_price_initialized = True
            line._update_price()

    @api.onchange('product_packaging_qty')
    def _onchange_packaging_qty(self):
        for line in self:
            line._update_price()

    @api.onchange('package_price','second_product_uom_qty')
    def _onchange_package_price(self):
        for line in self:
            line._update_price()

    

    def _update_price(self):
        for line in self:
            pieces_per_box = line.product_packaging_id.qty or 1.0
            line.price_unit = line.package_price / pieces_per_box if pieces_per_box else 0.0

    @api.constrains('product_packaging_qty')
    def _force_qty_no_rest(self):
        for record in self:
            if record.product_packaging_qty and not record.product_packaging_qty.is_integer():
                raise ValidationError("Boxes should be integer")

    @api.depends('display_type', 'product_id', 'product_packaging_qty', 'second_product_uom_qty')
    def _compute_product_uom_qty(self):
        for line in self:
            if line.display_type:
                line.product_uom_qty = 0.0
                continue
            if not line.product_packaging_id:
                continue
            packaging_uom = line.product_packaging_id.product_uom_id
            qty_per_packaging = line.product_packaging_id.qty
            product_uom_qty = packaging_uom._compute_quantity(
                line.product_packaging_qty * qty_per_packaging, line.product_uom)
            line.product_uom_qty = product_uom_qty + line.second_product_uom_qty

    @api.onchange('second_product_uom_qty', 'product_packaging_id')
    def _restrict_qty_exceed_box(self):
        if self.product_packaging_id and self.second_product_uom_qty:
            package_qty = self.product_packaging_id.qty
            if self.second_product_uom_qty >= package_qty:
                raise ValidationError("Qty exceed box qty limit in place of it just increment the boxes qty.")

    

    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_id_check_stock(self):
        if self.product_id and self.product_uom_qty:
            qty_available = self.product_id.qty_available
            if self.product_uom_qty > qty_available:
                raise UserError(
                    f"The selected product '{self.product_id.display_name}' is out of stock. "
                    f"Only {qty_available} unit(s) available."
                )

    @api.constrains('product_id', 'product_uom_qty')
    def _check_product_stock(self):
        for line in self:
            if line.product_id.type == 'product':
                qty_available = line.product_id.qty_available
                if line.product_uom_qty > qty_available:
                    raise ValidationError(
                        f"Cannot confirm order. Product '{line.product_id.display_name}' "
                        f"has only {qty_available} unit(s) in stock."
                    )
