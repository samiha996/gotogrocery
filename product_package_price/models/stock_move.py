from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    package_qty = fields.Float(string="Package Quantity")
    pieces_qty = fields.Float(string="Pieces Quantity")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'package_qty' not in vals and vals.get('sale_line_id'):
                sale_line = self.env['sale.order.line'].browse(vals['sale_line_id'])
                vals['package_qty'] = sale_line.product_packaging_qty
                vals['pieces_qty'] = sale_line.second_product_uom_qty or 0.0
        return super().create(vals_list)
