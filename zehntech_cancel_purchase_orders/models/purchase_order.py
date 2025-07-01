from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    cancel_associated_records = fields.Boolean(
        string="Cancel Associated Records",
        help="Cancel associated receipts and bills when canceling the purchase order."
    )
    active = fields.Boolean(string='Active', default=True)

    def open_cancel_wizard(self):
        self._check_access()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Cancel Purchase Order'),
            'res_model': 'purchase.order.cancel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_option': 'cancel_only'},
        }

    def action_cancel_only(self):
        self._check_access()
        for order in self:
            if order.state != 'cancel':
                order.write({'state': 'cancel'})
                order.message_post(body=_("The purchase order has been marked as 'Cancelled'."))
                self.env['cancel.purchase.data.history'].create({
                    'name': order.name,
                    'model': self._name,
                    'record_id': order.id,
                    'action_type': 'cancel',
                    'associated_data': str({
                        'receipts': order.picking_ids.ids,
                        'bills': order.invoice_ids.ids
                    }),
                    'timestamp': fields.Datetime.now(),
                    'user_id': self.env.user.id,
                    'state': 'cancelled',
                })
                if order.cancel_associated_records:
                    order._cancel_associated_records()

    def action_reset_to_draft(self):
        self._check_access()
        for order in self:
            if order.state != 'cancel':
                order.write({'state': 'cancel'})
                order.message_post(body=_("The purchase order has been cancelled."))
            order.write({'state': 'draft'})
            associated_data = {
                'receipts': order.picking_ids.ids,
                'bills': order.invoice_ids.ids,
            }
            self.env['cancel.purchase.data.history'].create({
                'name': order.name,
                'model': self._name,
                'record_id': order.id,
                'action_type': 'reset_to_draft',
                'associated_data': str(associated_data),
                'timestamp': fields.Datetime.now(),
                'user_id': self.env.user.id,
                'state': 'reset_to_draft',
            })
            if order.cancel_associated_records:
                order._reset_associated_records()
            order.message_post(body=_("The purchase order and associated records have been reset to Draft."))

    def action_cancel_and_delete(self):
        self._check_access()
        for order in self:
            if order.state != 'cancel':
                order.write({'state': 'cancel'})
            associated_data = {
                'name': order.name,
                'partner_id': order.partner_id.id,
                'order_line': [(0, 0, {
                    'product_id': line.product_id.id, 
                    'product_qty': line.product_qty
                }) for line in order.order_line],
                'state': 'draft',
            }
            self.env['cancel.purchase.data.history'].create({
                'name': order.name,
                'record_id': order.id,
                'action_type': 'delete',
                'associated_data': str(associated_data),
                'timestamp': fields.Datetime.now(),
                'user_id': self.env.user.id,
                'state': 'archived',
            })
            order.message_post(body=_("The purchase order has been archived to data history."))
            order.write({'active': False})

    def action_bulk_cancel_only(self):
        self._check_access()
        if self.env.context.get('dashboard_mode'):
            raise UserError(_("Bulk cancel actions are not allowed from the Dashboard."))
        self.action_cancel_only()

    def action_bulk_reset_to_draft(self):
        self._check_access()
        if self.env.context.get('dashboard_mode'):
            raise UserError(_("Bulk cancel actions are not allowed from the Dashboard."))
        self.action_reset_to_draft()

    def action_bulk_cancel_and_delete(self):
        self._check_access()
        if self.env.context.get('dashboard_mode'):
            raise UserError(_("Bulk cancel actions are not allowed from the Dashboard."))
        self.action_cancel_and_delete()

    def _cancel_associated_records(self):
        """
        For every receipt (picking) linked to this purchase order that is not in 'done',
        force it to cancel. This now applies to all states other than 'done'.
        """
        for picking in self.picking_ids:
            if picking.state != 'done':
                # If in 'ready' state, unreserve any reserved stock
                if picking.state == 'ready':
                    picking.do_unreserve()
                # Force the picking to cancel (using write is sometimes more reliable than action_cancel)
                picking.write({'state': 'cancel'})
                picking.message_post(body=_("This receipt was canceled along with the purchase order."))
            else:
                self.message_post(body=_("Receipt %s is already done and cannot be canceled." % picking.name))

        for bill in self.invoice_ids:
            if bill.state == 'draft':
                bill.button_cancel()
                bill.message_post(body=_("This bill was canceled along with the purchase order."))
            else:
                self.message_post(body=_("Bill %s is posted/paid and was not canceled." % bill.name))

    def _reset_associated_records(self):
        """
        For every receipt (picking) linked to this purchase order that is not in 'done',
        force it to reset to draft. This ensures that all receipts (even those in 'ready' state)
        are reverted.
        """
        for picking in self.picking_ids:
            if picking.state != 'done':
                # First, if not already canceled, unreserve and cancel it
                if picking.state != 'cancel':
                    picking.do_unreserve()
                    picking.write({'state': 'cancel'})
                # Then, reset it to draft
                picking.write({'state': 'draft'})
                # Reset moves if applicable
                move_field = 'move_lines' if hasattr(picking, 'move_lines') else 'move_ids_without_package'
                for move in getattr(picking, move_field, []):
                    if move.state == 'cancel':
                        move.write({'state': 'draft'})
                picking.message_post(body=_("This receipt was reset to draft along with the purchase order."))
            else:
                self.message_post(body=_("Receipt %s is already done and cannot be reset to draft." % picking.name))

        for bill in self.invoice_ids:
            if bill.state == 'cancel':
                bill.button_draft()
                bill.message_post(body=_("This bill was reset to draft along with the purchase order."))
            else:
                self.message_post(body=_("Bill %s is posted/paid and was not reset to draft." % bill.name))

    # def _delete_associated_records(self):
    #     for picking in self.picking_ids:
    #         if picking.state != 'cancel':
    #             picking.do_unreserve()
    #             picking.write({'state': 'cancel'})
    #         picking.unlink()
    #         self.message_post(body=_("Receipt %s was deleted along with the purchase order." % picking.name))

    #     for bill in self.invoice_ids:
    #         if bill.state == 'draft':
    #             bill.button_cancel()
    #             bill.unlink()
    #             self.message_post(body=_("Bill %s was deleted along with the purchase order." % bill.name))
    #         else:
    #             self.message_post(body=_("Bill %s is posted/paid and cannot be deleted." % bill.name))

    def _check_access(self):
        # Admin users bypass the cancellation restrictions
        if self.env.user.has_group('base.group_system'):
            return
        enable_cancel_purchase = self.env['ir.config_parameter'].sudo().get_param('cancel_purchase.enable_feature', default='False')
        if enable_cancel_purchase != 'True':
            raise UserError(_("Cancel functionality is globally disabled for regular users. Please contact your administrator."))

    def action_restore_order(self):
        """Restore the purchase order (unarchive it)."""
        if not self.active:
            self.write({'active': True, 'state': 'draft'})
            self.message_post(body=_("The purchase order has been restored from the archive."))
        else:
            raise UserError(_("The purchase order is already active and does not need restoration."))
