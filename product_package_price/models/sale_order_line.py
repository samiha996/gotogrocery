from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    new_qty = fields.Float(string="New Qty")
    package_price = fields.Float(string="Package Price")
    _package_price_initialized = fields.Boolean(default=False)

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
            line._update_qty_and_prices()

    @api.onchange('product_packaging_qty')
    def _onchange_packaging_qty(self):
        for line in self:
            line._update_qty_and_prices()

    @api.onchange('package_price')
    def _onchange_package_price(self):
        for line in self:
            line._update_qty_and_prices()

    @api.onchange('new_qty')
    def _onchange_new_qty(self):
        for line in self:
            if line.new_qty:
                line.product_uom_qty += line.new_qty

    def _update_qty_and_prices(self):
        for line in self:
            pieces_per_box = line.product_packaging_id.qty or 1.0
            num_boxes = line.product_packaging_qty or 0.0
            total_pieces = pieces_per_box * num_boxes

           
            line.product_uom_qty = total_pieces
            line.price_unit = line.package_price / pieces_per_box if pieces_per_box else 0.0
