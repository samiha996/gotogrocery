from odoo import models, fields, api, _
class PurchaseOrderCancelWizard(models.TransientModel):
    _name = 'purchase.order.cancel.wizard'
    _description = 'Purchase Order Cancel Wizard'

    option = fields.Selection([
        ('cancel_only', 'Cancel Only'),
        ('reset_to_draft', 'Cancel and Reset to RFQ'),
        ('cancel_and_delete', 'Cancel and Delete'),
    ], required=True, string="Cancel Option", default="cancel_only")

    def _display_notification(self, title, message, message_type='success'):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'type': message_type,
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

    def confirm_cancel_action(self):
        active_id = self.env.context.get('active_id')
        purchase_order = self.env['purchase.order'].browse(active_id)
        if self.option == 'cancel_only':
            purchase_order.action_cancel_only()
            return self._display_notification(
                title=_('Success'),
                message=_('The purchase order has been successfully cancelled.'),
            )
        elif self.option == 'reset_to_draft':
            if purchase_order.state == 'draft':
                return self._display_notification(
                    title=_('Already in Draft'),
                    message=_('The purchase order is already in draft state. No changes made.'),
                    message_type='warning',
                )
            purchase_order.action_reset_to_draft()
            return self._display_notification(
                title=_('Success'),
                message=_('The purchase order and associated records have been reset to Draft successfully.'),
            )
        elif self.option == 'cancel_and_delete':
            return {
                'type': 'ir.actions.act_window',
                'name': _('Confirm Deletion'),
                'res_model': 'purchase.order.confirm.delete.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'active_id': purchase_order.id,
                'default_confirmation_message': _('Are you sure you want to permanently delete this Purchase Order?'),
        },
            }
