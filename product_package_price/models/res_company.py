from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    purchase_discount_product_id = fields.Many2one(
        'product.product',
        string="Purchase Discount Product",
        help="Product used as a discount line in purchase orders.",
    )
