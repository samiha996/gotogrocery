from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    new_qty = fields.Float(string="New Qty")
    package_price = fields.Float(string="Package Price")
    new_qty_last = fields.Float(string="Last Qty", default=0.0)
    delta_qty = fields.Float(string="Delta Qty", compute="_compute_delta_qty", store=False)

    _package_price_initialized = fields.Boolean(string="Box Price Initialized", default=False)

    def _prepare_account_move_line(self, move=False):
        res = super()._prepare_account_move_line(move)
        res['package_qty'] = self.product_packaging_qty
        res['pieces_qty'] = self.new_qty or 0.0
        return res
    
    def _prepare_stock_moves(self, picking):
        moves = super()._prepare_stock_moves(picking)
        for move in moves:
            move.update({
                'package_qty': self.product_packaging_qty,
                'pieces_qty': self.new_qty or 0.0
            })
        return moves

    

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
            # line.price_subtotal = line.package_price * boxes

    @api.depends('new_qty', 'new_qty_last')
    def _compute_delta_qty(self):
        for line in self:
            line.delta_qty = line.new_qty - line.new_qty_last

    @api.onchange('new_qty')
    def _onchange_new_qty(self):
        for line in self:
            delta = line.new_qty - line.new_qty_last
            print(f"[PO] New Qty: {line.new_qty}, Last Qty: {line.new_qty_last}, Delta: {delta}")
            line.product_qty += delta

    def write(self, vals):
        res = super().write(vals)
        for line in self:
            if 'new_qty' in vals:
                line.new_qty_last = line.new_qty
        return res

    def create(self, vals_list):
        for vals in vals_list:
            vals['new_qty_last'] = vals.get('new_qty', 0.0)
        return super().create(vals_list)

    @api.onchange('product_id')
    def _onchange_product_id_set_first_packaging(self):
        for line in self:
            if line.product_id and not line.product_packaging_id:
                if line.product_id.packaging_ids:
                    # Set the first packaging as default
                    line.product_packaging_id = line.product_id.packaging_ids[0]
                    
