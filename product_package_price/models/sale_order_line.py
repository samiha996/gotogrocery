# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    new_qty = fields.Float(string="New Qty")

    @api.onchange('new_qty')
    def _onchange_new_qty(self):
        for line in self:
            if line.new_qty:
                line.product_uom_qty += line.new_qty


    @api.depends('product_id', 'product_uom', 'product_uom_qty', 'product_packaging_id',)
    def _compute_price_unit(self):
        super()._compute_price_unit()
        for line in self:
            if line.product_packaging_id and line.product_packaging_id.unit_price:
                line.price_unit = line.product_packaging_id.unit_price
            else:
                line.price_unit = line.price_unit

    
    @api.onchange('product_packaging_id')
    def _onchange_product_packaging_id(self):
        if self.product_packaging_id and self.product_packaging_id.qty:
            self.product_uom_qty = self.product_packaging_id.qty
        else:
            self.product_uom_qty = self.product_uom_qty
