# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class LoanIssueLine(models.Model):
    _inherit = "loan.issue.line"

    structure = fields.Many2one(
        comodel_name="res.partner",
        string="Platform Structure",
        related="loan_issue_id.structure",
        store=True,
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

    @api.model
    def create(self, vals):
        if "structure" not in vals:
            vals["structure"] = self.env.user.structure.id
        line = super(LoanIssueLine, self).create(vals)

        # todo bring back to easy_my_coop_loan
        confirmation_mail_template = (
            line._get_loan_loan_subscription_received_mail_template()
        )
        confirmation_mail_template.send_mail(line.id)

        return line

    def _get_loan_loan_subscription_received_mail_template(self):
        return self.env["mail.template"].get_email_template_by_key(
            "loan_subscription_received", self.structure
        )

    def _get_loan_sub_mail_template(self):
        return self.env["mail.template"].get_email_template_by_key(
            "loan_sub_conf", self.structure
        )

    def _get_loan_pay_req_mail_template(self):
        return self.env["mail.template"].get_email_template_by_key(
            "loan_payment_req", self.structure
        )

    @api.multi
    def get_confirm_paid_email_template(self):
        self.ensure_one()
        return self.env["mail.template"].get_email_template_by_key(
            "loan_payment_received", self.structure
        )
