# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ShareLine(models.Model):
    _inherit = "share.line"

    def default_structure(self):
        return self.env.user.structure

    structure = fields.Many2one(
        comodel_name="res.partner",
        string="Platform Structure",
        domain=[("is_platform_structure", "=", True)],
        default=default_structure,
    )
    creation_mode = fields.Selection(
        [("auto", "Automatic"), ("manual", "Manual")],
        string="Creation mode",
        default="auto",
        readonly=True,
        help=(
            "'auto' means created by system, 'manual' means manually "
            "created by a user."
        ),
    )
