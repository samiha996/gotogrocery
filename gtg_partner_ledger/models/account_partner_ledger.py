from odoo import models, fields

class AccountPartnerLedger(models.TransientModel):
    _inherit = 'account.report.partner.ledger'

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        domain=[('parent_id', '=', False)],
        help="Optional: choose a single partner to filter the ledger report",
    )
    print('>>>>>>>>>>>..............partner_id',partner_id)

    def pre_print_report(self, data):
        data = super().pre_print_report(data)
        data['form'].update(self.read(['partner_id'])[0])
        return data

    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update({
            'reconciled': self.reconciled,
            'amount_currency': self.amount_currency,
            'partner_id': self.partner_id.id if self.partner_id else False,
        })
        print('..........................>>>>>>data', data)
        return self.env.ref('base_accounting_kit.action_report_partnerledger').report_action(self, data=data)
