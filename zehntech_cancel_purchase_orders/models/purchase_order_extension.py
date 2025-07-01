from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    date_only = fields.Date(
        string='Order Date (Date Only)',
        compute='_compute_date_only',
        store=True,
        help="Date part of the order date (converted to the user's local time)."
    )

    @api.depends('date_order')
    def _compute_date_only(self):
        for order in self:
            if order.date_order:
                # Convert the date_order to the user's local time then take the date part
                local_dt = fields.Datetime.context_timestamp(order, order.date_order)
                order.date_only = local_dt.date()
            else:
                order.date_only = False
