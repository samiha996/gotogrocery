from odoo import models, fields, api, _
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_feature = fields.Boolean(
        string="Enable Cancel Purchase for Users",
        config_parameter="cancel_purchase.enable_feature",
        help="Enable or disable cancel functionalities for non-admin users."
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        enable_feature = self.env['ir.config_parameter'].sudo().get_param('cancel_purchase.enable_feature', default='False')
        res.update(enable_feature=(enable_feature == 'True'))
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('cancel_purchase.enable_feature', self.enable_feature)
