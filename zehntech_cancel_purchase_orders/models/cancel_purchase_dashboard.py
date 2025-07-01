import logging
import json
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from datetime import timedelta
import json
import logging

_logger = logging.getLogger(__name__)

TIME_RANGE_SELECTION = [
    ('all_time', 'All Time'),
    ('today', 'Today'),
    ('this_week', 'This Week'),
    ('this_month', 'This Month'),
    ('this_quarter', 'This Quarter'),
    ('this_year', 'This Year'),
    ('custom', 'Custom'),
]

class CancelPurchaseDashboard(models.Model):
    _name = 'cancel.purchase.dashboard'
    _description = 'Cancel Purchase Dashboard'

    # Basic fields
    employee_id = fields.Many2one('res.users', string='User', required=False , ondelete='cascade', )
    color = fields.Char(string="Card Color", default="#000000")

    # Computed counts
    draft_count = fields.Integer(string="RFQ Count", compute="_compute_counts")
    confirmed_count = fields.Integer(string="Purchase Order Count", compute="_compute_counts")
    cancelled_count = fields.Integer(string="Cancelled Count", compute="_compute_counts")

    # JSON chart data for the standard Odoo dashboard_graph widget
    purchase_kanban_bar_chart = fields.Text(string="Purchase Bar Chart", compute="_compute_bar_json")

    # Simple HTML-based bar
    purchase_bar_html = fields.Html(string="Colored Bar Graph", compute="_compute_purchase_bar_html")

    # Optional color fields for each segment
    rfq_color = fields.Char(string="RFQ Color", default="#71639e")
    purchase_order_color = fields.Char(string="Purchase Order Color", default="#2ecc71")
    cancelled_color = fields.Char(string="Cancelled Color", default="#e74c3c")

    # Time filters
    time_range = fields.Selection(
        selection=TIME_RANGE_SELECTION,
        string="Time Range",
        default="all_time",
        help="Select a time range for the dashboard."
    )
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")

    icon_image = fields.Binary("Dashboard Image", help="Upload an image to use as the icon for the global dashboard card.", attachment=True)
    record_id_int = fields.Integer(string="Record ID", compute="_compute_record_id_int")
    selected_date_range = fields.Char(string="Selected Date Range", compute="_compute_selected_date_range", store=False)

    @api.depends_context('time_range', 'date_start', 'date_end')
    def _compute_selected_date_range(self):
        for record in self:
            if record.time_range == 'custom':
                if record.date_start and record.date_end:
                    record.selected_date_range = _("From %s to %s") % (record.date_start, record.date_end)
                elif record.date_start:
                    record.selected_date_range = _("From %s") % record.date_start
                elif record.date_end:
                    record.selected_date_range = _("Until %s") % record.date_end
                else:
                    record.selected_date_range = _("Custom Date Range")
            else:
                record.selected_date_range = ""

    @api.depends()
    def _compute_record_id_int(self):
        for rec in self:
            rec.record_id_int = rec.id

    @api.model
    def init(self):
        """Ensure a global dashboard record (employee_id=False) exists."""
        self.create_global_dashboard()

    @api.model
    def create_global_dashboard(self):
        """Create the global aggregated dashboard if none exists."""
        global_dashboard = self.search([('employee_id', '=', False)], limit=1)
        if not global_dashboard:
            self.create({'color': "#000000"})
            _logger.info("Global aggregated purchase dashboard created.")

    # ----------------------------------------
    # Compute the counts
    # ----------------------------------------
    @api.depends_context('time_range', 'date_start', 'date_end')
    def _compute_counts(self):
        PurchaseOrder = self.env['purchase.order']
        for record in self:
            domain = record._get_time_domain()
            # If it's a user-specific card
            if record.employee_id:
                domain.append(('user_id', '=', record.employee_id.id))

            # Count states
            record.draft_count = PurchaseOrder.search_count(domain + [('state', '=', 'draft')])
            record.confirmed_count = PurchaseOrder.search_count(domain + [('state', '=', 'purchase')])
            record.cancelled_count = PurchaseOrder.search_count(domain + [('state', '=', 'cancel')])
    def action_open_custom_range_wizard(self):
        self.ensure_one()
        return {
        'type': 'ir.actions.act_window',
        'res_model': 'cancel.purchase.date.range.wizard',
        'view_mode': 'form',
        'target': 'new',
        'name': _('Set Custom Date Range'),
        'context': {
            'default_dashboard_id': self.id,
            # If the user has an existing date range, pre-fill it
            'default_start_date': self.date_start,
            'default_end_date': self.date_end,
        },
    }
    def action_edit_icon(self):
        """Open the form view to edit the global dashboard icon."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Edit Global Dashboard Image'),
            'res_model': 'cancel.purchase.dashboard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
    # ----------------------------------------
    # Chart JSON (dashboard_graph widget)
    # ----------------------------------------
    def _compute_bar_chart(self):
        for record in self:
            data = [
                {"label": _("RFQ"), "value": record.draft_count, "color": record.rfq_color or "#71639e"},
                {"label": _("Purchase Order"), "value": record.confirmed_count, "color": record.purchase_order_color or "#2ecc71"},
                {"label": _("Cancelled"), "value": record.cancelled_count, "color": record.cancelled_color or "#e74c3c"},
            ]
            chart_data = {
                "values": data,
                "title": _("Purchase Order Status Overview"),
                "key": _("Total Orders"),
                "is_sample_data": False,
            }
            record.purchase_kanban_bar_chart = json.dumps(chart_data)

    # ----------------------------------------
    # Simple HTML-based bar (if needed)
    # ----------------------------------------
    def _compute_purchase_bar_html(self):
        for record in self:
            total = record.draft_count + record.confirmed_count + record.cancelled_count
            if total:
                rfq_pct = (record.draft_count / total) * 100
                purchase_pct = (record.confirmed_count / total) * 100
                cancelled_pct = (record.cancelled_count / total) * 100
            else:
                rfq_pct = purchase_pct = cancelled_pct = 0
            record.purchase_bar_html = f"""
               <div style="display: flex; height: 20px; width: 100%; border: 1px solid #ccc;">
                   <div style="background-color: {record.rfq_color}; width: {rfq_pct}%;"></div>
                   <div style="background-color: {record.purchase_order_color}; width: {purchase_pct}%;"></div>
                   <div style="background-color: {record.cancelled_color}; width: {cancelled_pct}%;"></div>
               </div>
               <div style="text-align: center; font-size: 12px; margin-top: 2px;">
                   {_("RFQ")}: {record.draft_count} | {_("Purchase Order")}: {record.confirmed_count} | {_("Cancelled")}: {record.cancelled_count}
               </div>
            """
    def action_save_icon(self):
        """Save the new icon (already in self.icon_image)."""
        self.ensure_one()
        _logger.info("DEBUG: icon_image size = %s", len(self.icon_image or b''))

        return {'type': 'ir.actions.act_window_close'}
    
    # ----------------------------------------
    # Time range domain
    # ----------------------------------------
    def _get_time_domain(self):
        """
        Build a domain on sale.order.date_order based on time filters.
        Looks at self.time_range, self.date_start, self.date_end, or fallback to context.
        """
        ctx = self.env.context
        time_range = ctx.get('time_range', self.time_range or 'all_time')
        date_start = ctx.get('date_start', self.date_start)
        date_end = ctx.get('date_end', self.date_end)
        domain = []
        today = fields.Date.today()

        if time_range == 'all_time':
            pass
        elif time_range == 'today':
            tomorrow = today + timedelta(days=1)
            domain = [('date_order', '>=', today), ('date_order', '<', tomorrow)]
        elif time_range == 'this_week':
            weekday = today.weekday()  # Monday=0
            start_of_week = today - timedelta(days=weekday)
            end_of_week = start_of_week + timedelta(days=7)
            domain = [('date_order', '>=', start_of_week), ('date_order', '<', end_of_week)]
        elif time_range == 'this_month':
            start_of_month = today.replace(day=1)
            if today.month == 12:
                next_month = today.replace(year=today.year + 1, month=1, day=1)
            else:
                next_month = today.replace(month=today.month + 1, day=1)
            domain = [('date_order', '>=', start_of_month), ('date_order', '<', next_month)]
        elif time_range == 'this_quarter':
            month = today.month
            quarter = (month - 1) // 3 + 1
            start_month = 3 * (quarter - 1) + 1
            start_of_quarter = today.replace(month=start_month, day=1)
            if start_month == 10:
                # next quarter is Jan 1 of next year
                next_quarter = start_of_quarter.replace(year=start_of_quarter.year + 1, month=1, day=1)
            else:
                next_quarter = start_of_quarter.replace(month=start_month + 3, day=1)
            domain = [('date_order', '>=', start_of_quarter), ('date_order', '<', next_quarter)]
        elif time_range == 'this_year':
            start_of_year = today.replace(month=1, day=1)
            next_year = start_of_year.replace(year=start_of_year.year + 1)
            domain = [('date_order', '>=', start_of_year), ('date_order', '<', next_year)]
        elif time_range == 'custom':
            # Use date_start / date_end
            if date_start:
                domain.append(('date_order', '>=', date_start))
            if date_end:
                domain.append(('date_order', '<=', date_end))

        return domain
    
    @api.depends_context('time_range', 'date_start', 'date_end')
    def _compute_counts(self):
        PurchaseOrder = self.env['purchase.order']
        for record in self:
            # 1) Get the date domain from your custom logic
            date_domain = record._get_time_domain()

            # 2) If there's an employee, add user_id to the domain
            if record.employee_id:
                date_domain.append(('user_id', '=', record.employee_id.id))

            # 3) Use this combined domain to compute each count
            record.draft_count = PurchaseOrder.search_count(date_domain + [('state', '=', 'draft')])
            record.confirmed_count = PurchaseOrder.search_count(date_domain + [('state', '=', 'purchase')])
            record.cancelled_count = PurchaseOrder.search_count(date_domain + [('state', '=', 'cancel')])
    def _compute_chart_json(self):
        for record in self:
            data = [
                {"label": _("Quotation"), "value": record.draft_count, "color": record.quotation_color or "#3498db"},
                {"label": _("Purchase Order"), "value": record.confirmed_count, "color": record.purchase_order_color or "#2ecc71"},
                {"label": _("Cancelled"), "value": record.cancelled_count, "color": record.cancelled_color or "#e74c3c"},
            ]
            chart_data = {
                "values": data,
                "title": _("Purchase Order Status Overview"),
                "key": _("Total Orders"),
                "is_sample_data": False,
            }
            record.purchase_kanban_bar_chart = json.dumps(chart_data)

    def action_open_draft_records(self):
        domain = self._get_time_domain() + [('state', '=', 'draft')]
        if self.employee_id:
            domain.append(('user_id', '=', self.employee_id.id))
        return {
            'name': _('RFQ Purchase Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'tree',
            'views': [
                (self.env.ref('zehntech_cancel_purchase_orders.view_purchase_order_tree_no_bulk_actions').id, 'tree'),
            ],
            'domain': domain,
            'context': {
                'create': False,
                'dashboard_mode': True,
            },
        }

    def action_open_confirmed_records(self):
        """Open confirmed purchase orders respecting the time range filter."""
        domain = self._get_time_domain() + [('state', '=', 'purchase')]
        if self.employee_id:
            domain.append(('user_id', '=', self.employee_id.id))
        return {
            'name': _('Confirmed Purchase Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'tree',
            'views': [
                (self.env.ref('zehntech_cancel_purchase_orders.view_purchase_order_tree_no_bulk_actions').id, 'tree'),
            ],
            'domain': domain,
            'context': {
                'create': False,
                'dashboard_mode': True,
            },
        }

    def action_open_cancelled_records(self):
        """Open cancelled purchase orders respecting the time range filter."""
        domain = self._get_time_domain() + [('state', '=', 'cancel')]
        if self.employee_id:
            domain.append(('user_id', '=', self.employee_id.id))
        return {
            'name': _('Cancelled Purchase Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'tree',
            'views': [
                (self.env.ref('zehntech_cancel_purchase_orders.view_purchase_order_tree_no_bulk_actions').id, 'tree'),
            ],
            'domain': domain,
            'context': {
                'create': False,
                'dashboard_mode': True,
            },
        }

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):
        if not isinstance(vals_list, list):
            vals_list = [vals_list]
        users = super().create(vals_list)
        dashboards_to_create = []
        for user in users:
            dashboards_to_create.append({
                'employee_id': user.id,
                'color': "#%06x" % (int(user.id) * 56789 % 0xFFFFFF),
            })
        self.env['cancel.purchase.dashboard'].create_global_dashboard()
        _logger.info("Creating %s dashboard records for new users.", len(dashboards_to_create))
        self.env['cancel.purchase.dashboard'].create(dashboards_to_create)
        return users
