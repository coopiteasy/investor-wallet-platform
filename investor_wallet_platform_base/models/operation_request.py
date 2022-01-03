# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class OperationRequest(models.Model):
    _inherit = "operation.request"

    def default_structure(self):
        return self.env.user.structure

    structure = fields.Many2one(
        comodel_name="res.partner",
        string="Platform Structure",
        domain=[("is_platform_structure", "=", True)],
        default=default_structure,
    )

    def _get_share_transfer_mail_template(self):
        return self.env["mail.template"].get_email_template_by_key(
            "certificate_trans", self.structure
        )

    def _get_share_update_mail_template(self):
        templ_obj = self.env["mail.template"]
        return templ_obj.get_email_template_by_key(
            "share_update", self.structure
        )

    def _send_share_transfer_email(self, sub_register_line):
        if not self.structure.is_delegated_to_api_client:
            cert_email_template = self._get_share_transfert_mail_template()
            # TODO this will need a dedicated certificate report
            cert_email_template.send_mail(sub_register_line.id, False)

    def _send_share_update_email(self, sub_register_line):
        if not self.structure.is_delegated_to_api_client:
            cert_email_template = self._get_share_update_mail_template()
            cert_email_template.send_mail(sub_register_line.id, False)

    def get_subscription_register_vals(self, effective_date):
        vals = super(OperationRequest, self).get_subscription_register_vals(
            effective_date
        )
        vals["structure"] = self.structure.id
        return vals

    def get_total_share_dic(self, partner):
        share_products = self.env["product.template"].search(
            [("is_share", "=", True), ("structure", "=", self.structure.id)]
        )
        # Init total_share_dic
        total_share_dic = {}
        for share_product in share_products:
            total_share_dic[share_product.id] = 0

        shares = partner.share_ids.filtered(
            lambda r: (
                r.structure == self.structure and r.creation_mode == "auto"
            )
        )
        for line in shares:
            total_share_dic[line.share_product_id.id] += line.share_number
        return total_share_dic

    def hand_share_over(self, partner, share_product_id, quantity):
        membership = partner.get_membership(self.structure)
        if not membership.member:
            raise ValidationError(
                _(
                    "This operation can't be executed if the"
                    " cooperator is not an effective member"
                )
            )

        owned_shares = partner.share_ids.filtered(
            lambda r: (
                r.structure == self.structure and r.creation_mode == "auto"
            )
        )
        share_ind = len(owned_shares)
        i = 1
        while quantity > 0:
            line = owned_shares[share_ind - i]
            if line.share_product_id.id == share_product_id.id:
                if quantity > line.share_number:
                    quantity -= line.share_number
                    line.unlink()
                else:
                    share_left = line.share_number - quantity
                    quantity = 0
                    line.write({"share_number": share_left})
            i += 1
        # if the cooperator sold all his shares he's no more
        # an effective member
        remaning_share_dict = 0
        for share_quant in self.get_total_share_dic(partner).values():
            remaning_share_dict += share_quant
        if remaning_share_dict == 0:
            membership.write({"member": False, "old_member": True})
