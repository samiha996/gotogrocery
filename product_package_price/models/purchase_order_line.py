from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    package_price = fields.Float(string="Package Price")
    _package_price_initialized = fields.Boolean(default=False)

    second_product_uom_qty = fields.Float()

    product_packaging_qty = fields.Float(
        string="Packaging Quantity",
        compute=False,
        store=True, readonly=False, precompute=True)

    product_qty = fields.Float(
        string="Quantity",
        compute='_compute_product_qty',
        digits='Product Unit of Measure', default=False,
        store=True, readonly=False, required=True, precompute=True)

    price_unit = fields.Float(
        string='Unit Price',
        compute='_update_price',
        digits='Product Price', default=0.0,
        store=True, readonly=False, precompute=True)

    def _prepare_account_move_line(self, move=False):
        res = super()._prepare_account_move_line(move)
        res['package_qty'] = self.product_packaging_qty
        res['pieces_qty'] = self.second_product_uom_qty or 0.0
        return res

    def _prepare_stock_moves(self, picking):
        moves = super()._prepare_stock_moves(picking)
        for move in moves:
            move.update({
                'package_qty': self.product_packaging_qty,
                'pieces_qty': self.second_product_uom_qty or 0.0
            })
        return moves

    @api.onchange('product_id')
    def _onchange_product_id_set_first_packaging(self):
        for line in self:
            if line.product_id and not line.product_packaging_id and line.product_id.packaging_ids:
                line.product_packaging_id = line.product_id.packaging_ids[0]

            # Set default package price
            if line.product_packaging_id and not line._package_price_initialized:
                line.package_price = line.product_packaging_id.package_price or 0.0
                line._package_price_initialized = True

            # 💡 Force recompute of quantities manually
            line._compute_product_qty()
            line._update_price()

    @api.onchange('product_packaging_id')
    def _onchange_product_packaging_id(self):
        for line in self:
            if line.product_packaging_id and not line._package_price_initialized:
                line.package_price = line.product_packaging_id.package_price or 0.0
                line._package_price_initialized = True
            line._update_price()

    @api.onchange('product_packaging_qty')
    def _onchange_packaging_qty(self):
        for line in self:
            line._update_price()

    @api.onchange('package_price', 'second_product_uom_qty')
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
    def _compute_product_qty(self):
        for line in self:
            if line.display_type:
                line.product_qty = 0.0
                continue
            if not line.product_packaging_id:
                continue
            packaging_uom = line.product_packaging_id.product_uom_id
            qty_per_packaging = line.product_packaging_id.qty
            product_qty = packaging_uom._compute_quantity(
                line.product_packaging_qty * qty_per_packaging, line.product_uom)
            line.product_qty = product_qty + line.second_product_uom_qty

    @api.onchange('second_product_uom_qty', 'product_packaging_id')
    def _restrict_qty_exceed_box(self):
        if self.product_packaging_id and self.second_product_uom_qty:
            package_qty = self.product_packaging_id.qty
            if self.second_product_uom_qty >= package_qty:
                raise ValidationError("Qty exceed box qty limit. Instead, increase the number of boxes.")

    
    def _compute_price_unit_and_date_planned_and_name(self):
        super()._compute_price_unit_and_date_planned_and_name()

        for line in self:
            # If package price is used, always apply custom price logic
            if line.package_price and line.product_packaging_id:
                pieces_per_box = line.product_packaging_id.qty or 1.0
                line.price_unit = line.package_price / pieces_per_box if pieces_per_box else 0.0
