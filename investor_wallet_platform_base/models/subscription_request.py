# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SubscriptionRequest(models.Model):
    _inherit = "subscription.request"

    def default_structure(self):
        return self.env.user.structure

    structure = fields.Many2one(
        comodel_name="res.partner",
        string="Platform Structure",
        domain=[("is_platform_structure", "=", True)],
        default=default_structure,
    )

    def get_structure_email_template_notif(self, is_company=False):
        if is_company:
            mail_template = "investor_wallet_platform_base.email_template_notification_company"
        else:
            mail_template = (
                "investor_wallet_platform_base.email_template_notification"
            )
        return self.env.ref(mail_template, False)

    def get_mail_template_notif(self, is_company=False):
        templ_obj = self.env["mail.template"]
        if is_company:
            return templ_obj.get_email_template_by_key(
                "sub_req_comp_notif", self.structure
            )
        else:
            return templ_obj.get_email_template_by_key(
                "sub_req_notif", self.structure
            )

    def get_capital_release_mail_template(self):
        template_obj = self.env["mail.template"]
        return template_obj.get_email_template_by_key(
            "rel_capital", self.structure
        )

    @api.model
    def create(self, vals):
        subscr_request = super(SubscriptionRequest, self).create(vals)
        notification_template = subscr_request.get_structure_email_template_notif(
            False
        )
        notification_template.send_mail(subscr_request.id)
        return subscr_request

    @api.model
    def create_comp_sub_req(self, vals):
        subscr_request = super(SubscriptionRequest, self).create_comp_sub_req(
            vals
        )
        notification_template = subscr_request.get_structure_email_template_notif(
            True
        )
        notification_template.send_mail(subscr_request.id)
        return subscr_request

    def get_journal(self):
        if self.structure:
            if self.structure.account_journal:
                return self.structure.account_journal
            else:
                raise ValidationError(
                    _("There is no journal defined for this " "structure.")
                )
        else:
            raise ValidationError(
                _(
                    "There is no structure defined on this "
                    "subscription request."
                )
            )

    def get_invoice_vals(self, partner):
        vals = super(SubscriptionRequest, self).get_invoice_vals(partner)
        vals["structure"] = self.structure.id

        return vals

    def is_member(self, vals, cooperator):
        membership = cooperator.get_membership(self.structure)

        if membership and membership.member:
            vals["type"] = "increase"
            vals["already_cooperator"] = True
        return vals

    def set_membership(self):
        member_obj = self.env["coop.membership"]
        membership = self.partner_id.get_membership(self.structure)
        if not membership:
            vals = {
                "structure": self.structure.id,
                "partner_id": self.partner_id.id,
            }
            member_obj.create(vals)
        return True
