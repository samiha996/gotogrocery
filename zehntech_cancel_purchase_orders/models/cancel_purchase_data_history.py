from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CancelPurchaseDataHistory(models.Model):
    _name = 'cancel.purchase.data.history'
    _description = 'Cancel Purchase Data History'

    name = fields.Char(string="Record Name", required=True)
    model = fields.Char(string="Model", default='purchase.order')
    record_id = fields.Integer(string="Record ID", required=True)
    user_id = fields.Many2one('res.users', string="Performed By", default=lambda self: self.env.user, required=True)
    action_type = fields.Selection(
        [('cancel', 'Cancel'), ('delete', 'Delete'), ('reset_to_draft', 'Reset to Draft')],
        string="Action Type",
        required=True
    )
    associated_data = fields.Text(string="Associated Data", help="Serialized data for related fields")
    timestamp = fields.Datetime(string="Timestamp", default=fields.Datetime.now)
    state = fields.Selection([
        ('archived', 'Deleted'),
        ('restored', 'Restored'),
        ('reset_to_draft', 'Reset to Draft'),
        ('cancelled', 'Cancelled'),
    ], default='archived', string="State")

    def restore_data(self):
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_("Only administrators can restore data history."))

        for record in self:
            if record.state != 'archived':
                raise UserError(_("Only deleted records can be restored."))

            associated_data = eval(record.associated_data or '{}')
            receipts = associated_data.get('receipts', [])
            bills = associated_data.get('bills', [])

            purchase_order = self.env['purchase.order'].search([('id', '=', record.record_id), ('active', '=', False)])
            if not purchase_order:
                raise UserError(_("The purchase order record could not be found or is already active."))

            purchase_order.write({'active': True, 'state': 'draft'})
            purchase_order.message_post(body=_("The purchase order has been restored from the archive."))

            for picking_id in receipts:
                picking = self.env['stock.picking'].browse(picking_id)
                if picking.exists() and not picking.active:
                    picking.write({'active': True, 'state': 'draft'})
                    picking.message_post(body=_("This receipt was restored along with the purchase order."))

            for bill_id in bills:
                bill = self.env['account.move'].browse(bill_id)
                if bill.exists() and not bill.active:
                    bill.write({'active': True, 'state': 'draft'})
                    bill.message_post(body=_("This bill was restored along with the purchase order."))

            record.write({'state': 'restored'})

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('The purchase order and associated records have been restored successfully.'),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.client', 'tag': 'reload'},
            },
        }
