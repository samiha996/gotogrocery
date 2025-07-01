from odoo import models, fields, api, _

from odoo.exceptions import UserError

class CancelPurchaseDateRangeWizard(models.TransientModel):

    _name = 'cancel.purchase.date.range.wizard'

    _description = 'Cancel Purchase Custom Date Range Wizard'

    dashboard_id = fields.Many2one('cancel.purchase.dashboard', string="Dashboard", required=True)

    start_date = fields.Date(string="Start Date")

    end_date = fields.Date(string="End Date")

    @api.onchange('start_date', 'end_date')

    def _check_dates(self):

        """Prevent user from picking start_date > end_date."""

        if self.start_date and self.end_date and self.start_date > self.end_date:

            raise UserError(_("Start Date cannot be after End Date."))

    def action_apply_date_range(self):

        """Set the time_range='custom' and store the selected dates on the dashboard."""

        self.ensure_one()

        self.dashboard_id.write({

            'time_range': 'custom',

            'date_start': self.start_date,

            'date_end': self.end_date,

        })

        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_clear_date_range(self):

        """

        Reset the dashboard to 'all_time' and clear any saved start/end dates.

        """

        self.ensure_one()

        self.dashboard_id.write({

            'time_range': 'all_time',

            'date_start': False,

            'date_end': False,

        })

        return {'type': 'ir.actions.client', 'tag': 'reload'} 