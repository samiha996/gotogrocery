from odoo import models, fields, api, _

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    representative_name = fields.Char(string="Representative Name")
    customer_number = fields.Char(related='partner_id.customer_number', string="Customer Number", readonly=True, store=True)

    def action_open_discount_wizard(self):
        self.ensure_one()
        return {
            'name': _("Discount"),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order.discount',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }
