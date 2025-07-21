# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductPackage(models.Model):
    _inherit = 'product.packaging'

    package_price = fields.Float(
        digits='Product Price'
    )
    package_sale_price = fields.Float(
        digits='Product Price', string="SO Box Price",
    )
    unit_price = fields.Float(
        digits='Product Price',
        compute='_compute_unit_price',
        store=True
    )

    @api.depends('package_price', 'qty')
    def _compute_unit_price(self):
        for record in self:
            if record.package_price and record.qty:
                record.unit_price = record.package_price / record.qty
            else:
                record.unit_price = False
