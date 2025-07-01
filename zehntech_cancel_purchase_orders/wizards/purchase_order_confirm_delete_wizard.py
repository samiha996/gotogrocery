from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseOrderConfirmDeleteWizard(models.TransientModel):
    _name = 'purchase.order.confirm.delete.wizard'
    _description = 'Purchase Order Confirm Delete Wizard'

    confirmation_message = fields.Char(
        string=_("Confirmation Message"),
        readonly=True
    )

    def confirm_delete_action(self):
        active_id = self.env.context.get('active_id')
        purchase_order = self.env['purchase.order'].browse(active_id)

        if not purchase_order.exists():
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Warning'),
                    'message': _('The purchase order no longer exists.'),
                    'type': 'warning',
                    'sticky': False,
                },
            }

        purchase_order.action_cancel_and_delete()

        quotations_action = self.env.ref('purchase.purchase_rfq').sudo().read()[0]
        quotations_action['target'] = 'current'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('The purchase order has been successfully deleted.'),
                'type': 'success',
                'sticky': False,
                'next': quotations_action,
            },
        }
