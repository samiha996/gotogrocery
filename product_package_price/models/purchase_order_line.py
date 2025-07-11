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
                if not line._package_price_initialized:
                    line.package_price = line.product_packaging_id.package_price or 0.0
                    line._package_price_initialized = True
                line._compute_qty_and_price()

    @api.onchange('product_packaging_qty')
    def _onchange_packaging_qty(self):
        for line in self:
            line._compute_qty_and_price()

    @api.onchange('package_price')
    def _onchange_package_price(self):
        for line in self:
            line._compute_qty_and_price()

    @api.onchange('product_id')
    def _onchange_product_id_set_first_packaging(self):
        for line in self:
            if line.product_id:
                line.product_uom = line.product_id.uom_po_id.id
                if not line.product_packaging_id and line.product_id.packaging_ids:
                    line.product_packaging_qty = 1.0	
                    line.product_packaging_id = line.product_id.packaging_ids[0]
                if line.product_packaging_id and not line._package_price_initialized:
                    line.package_price = line.product_packaging_id.package_price or 0.0
                    line._package_price_initialized = True
                line.product_packaging_qty = 1.0
                line._compute_qty_and_price()

    def _compute_qty_and_price(self):
        for line in self:
            pieces_per_box = line.product_packaging_id.qty or 1.0
            boxes = line.product_packaging_qty or 1.0
            total_pieces = pieces_per_box * boxes
            line.product_qty = total_pieces
            if pieces_per_box:
                line.price_unit = line.package_price / pieces_per_box
            else:
                line.price_unit = line.package_price

    @api.onchange('product_id', 'product_packaging_id', 'product_packaging_qty', 'package_price')
    def _force_final_price_unit(self):
        """This onchange ensures price_unit override happens LAST, after Odoo changes."""
        for line in self:
            if line.product_packaging_id:
                pieces_per_box = line.product_packaging_id.qty or 1.0
                if pieces_per_box:
                    line.price_unit = line.package_price / pieces_per_box
                else:
                    line.price_unit = line.package_price

    @api.depends('new_qty', 'new_qty_last')
    def _compute_delta_qty(self):
        for line in self:
            line.delta_qty = line.new_qty - line.new_qty_last

    @api.onchange('new_qty')
    def _onchange_new_qty(self):
        for line in self:
            delta = line.new_qty - line.new_qty_last
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
    
    
    @api.depends('product_id', 'product_qty', 'product_uom', 'partner_id', 'currency_id')
    def _compute_price_unit_and_date_planned_and_name(self):
        for line in self:
            if not line.product_id or line.invoice_lines or not line.company_id:
                continue

            # Force date planned to today or based on your logic
            line.date_planned = fields.Datetime.now()

            # Custom pricing logic only
            pieces_per_box = line.product_packaging_id.qty or 1.0
            if pieces_per_box:
                line.price_unit = line.package_price / pieces_per_box
            else:
                line.price_unit = line.package_price

            # Preserve custom description if any
            if not line.name:
                product_lang = line.product_id.with_context(
                    lang=self.env.user.lang,
                    partner_id=None,
                    company_id=line.company_id.id,
                )
                line.name = line._get_product_purchase_description(product_lang)

            line.discount = 0.0  # disable vendor discount
