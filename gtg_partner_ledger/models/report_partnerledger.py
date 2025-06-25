from odoo import models
import time

from odoo.exceptions import UserError

class ReportPartnerLedger(models.AbstractModel):
    _inherit = 'report.base_accounting_kit.report_partnerledger'

    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError("Form content is missing, this report cannot be printed.")

        data['computed'] = {}
        obj_partner = self.env['res.partner']
        query_get_data = self.env['account.move.line'].with_context(
            data['form'].get('used_context', {}))._query_get()

        data['computed']['move_state'] = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            data['computed']['move_state'] = ['posted']

        result_selection = data['form'].get('result_selection', 'customer')
        if result_selection == 'supplier':
            data['computed']['ACCOUNT_TYPE'] = ['liability_payable']
        elif result_selection == 'customer':
            data['computed']['ACCOUNT_TYPE'] = ['asset_receivable']
        else:
            data['computed']['ACCOUNT_TYPE'] = ['liability_payable', 'asset_receivable']

        self.env.cr.execute("""
            SELECT a.id
            FROM account_account a
            WHERE a.account_type IN %s
            AND NOT a.deprecated
        """, (tuple(data['computed']['ACCOUNT_TYPE']),))
        data['computed']['account_ids'] = [a for (a,) in self.env.cr.fetchall()]

        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
        params = [tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]

        query = """
            SELECT DISTINCT "account_move_line".partner_id
            FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
            WHERE "account_move_line".partner_id IS NOT NULL
                AND "account_move_line".account_id = account.id
                AND am.id = "account_move_line".move_id
                AND am.state IN %s
                AND "account_move_line".account_id IN %s
                AND NOT account.deprecated
                AND """ + query_get_data[1] + reconcile_clause

        # ✅ Apply partner_id filter if selected
        if data['form'].get('partner_id'):
            partner_ids = [data['form']['partner_id']]
        else:
            self.env.cr.execute(query, tuple(params))
            partner_ids = [res['partner_id'] for res in self.env.cr.dictfetchall()]

        partners = obj_partner.browse(partner_ids)
        partners = sorted(partners, key=lambda x: (x.ref or '', x.name or ''))

        return {
            'doc_ids': partner_ids,
            'doc_model': self.env['res.partner'],
            'data': data,
            'docs': partners,
            'time': time,
            'lines': self._lines,
            'sum_partner': self._sum_partner,
        }
