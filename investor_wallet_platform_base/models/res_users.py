from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    structure = fields.Many2one(
        comodel_name="res.partner",
        string="Platform Structure",
        domain=[("is_platform_structure", "=", True)],
    )
