# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
#   Houssine Bakkali <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import fields, models, _
from odoo.exceptions import ValidationError

_EMAIL_TEMPLATE_IDS = {
    "sub_req_notif": "investor_wallet_platform_base.email_template_confirmation",
    "sub_req_comp_notif": "investor_wallet_platform_base.email_template_confirmation_company",
    "rel_capital": "investor_wallet_platform_base.email_template_release_capital",
    "certificate": "investor_wallet_platform_base.email_template_certificat",
    "certificate_inc": "investor_wallet_platform_base.email_template_certificat_increase",
    "certificate_trans": "investor_wallet_platform_base.email_template_share_transfer",
    "share_update": "investor_wallet_platform_base.email_template_share_update",
    "loan_subscription_received": "investor_wallet_platform_base.loan_subscription_received",
    "loan_sub_conf": "investor_wallet_platform_base.loan_subscription_confirmation",
    "loan_payment_req": "investor_wallet_platform_base.loan_issue_payment_request",
    "loan_payment_received": "investor_wallet_platform_base.email_template_loan_confirm_paid",
}


class MailTemplate(models.Model):
    _inherit = "mail.template"

    def _get_email_template_dict(self):
        return _EMAIL_TEMPLATE_IDS

    structure = fields.Many2one(
        comodel_name="res.partner",
        string="Platform Structure",
        domain=[("is_platform_structure", "=", True)],
    )
    template_key = fields.Char(string="Mail template key", readonly=True)
    iwp = fields.Boolean(string="IWP mail template")

    def get_email_template_by_key(
        self, mail_template_key, structure, raise_=True
    ):
        template_obj = self.env["mail.template"]
        mail_template = template_obj.search(
            [
                ("template_key", "=", mail_template_key),
                ("structure", "=", structure.id),
            ],
            limit=1,
        )

        if not mail_template and raise_:
            raise ValidationError(
                _("Please generate emails for your structure.")
            )

        return mail_template
