from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    new_qty = fields.Float(string="New Qty")
    package_price = fields.Float(string="Package Price")

    _package_price_initialized = fields.Boolean(string="Box Price Initialized", default=False)

    @api.onchange('product_packaging_id')
    def _onchange_product_packaging_id(self):
        for line in self:
            if line.product_packaging_id:
                # Set only the first time
                if not line._package_price_initialized:
                    line.package_price = line.product_packaging_id.package_price or 0.0
                    line._package_price_initialized = True

                line.product_qty = line.product_packaging_id.qty or 1.0

            line._recompute_custom_prices()

    @api.onchange('product_packaging_qty')
    def _onchange_packaging_qty(self):
        for line in self:
            line._recompute_custom_prices()

    @api.onchange('package_price')
    def _onchange_package_price(self):
        for line in self:
            line._recompute_custom_prices()

    def _recompute_custom_prices(self):
        for line in self:
            pieces_per_box = line.product_packaging_id.qty or 1.0
            boxes = line.product_packaging_qty or 1.0

            line.price_unit = line.package_price / pieces_per_box
            line.price_subtotal = line.package_price * boxes

    @api.onchange('new_qty')
    def _onchange_new_qty(self):
        for line in self:
            if line.new_qty:
                line.product_qty += line.new_qty

    @api.onchange('product_id')
    def _onchange_product_id_set_first_packaging(self):
        for line in self:
            if line.product_id and not line.product_packaging_id:
                if line.product_id.packaging_ids:
                    # Set the first packaging as default
                    line.product_packaging_id = line.product_id.packaging_ids[0]
                    
