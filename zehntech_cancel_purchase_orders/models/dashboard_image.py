import base64
from odoo import http
from odoo.http import request

class DashboardImageController(http.Controller):
    @http.route(['/dashboard_icon/<int:record_id>'], type='http', auth='public', csrf=False)
    def dashboard_icon(self, record_id, **kw):
        record = request.env['cancel.purchase.dashboard'].sudo().browse(record_id)
        if record and record.icon_image:
            image_data = base64.b64decode(record.icon_image)
            return request.make_response(
                image_data,
                headers=[
                    ('Content-Type', 'image/png'),
                    ('Content-Disposition', 'inline; filename="dashboard_icon.png"')
                ]
            )
        else:
            # Return a fallback image if no icon is found
            return request.redirect('/zehntech_cancel_purchase_orders/static/description/fallback.png')
