# Copyright 2018 Odoo SA <http://odoo.com>
# Copyright 2019-     Coop IT Easy SCRLfs <http://coopiteasy.be>
#     - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from itertools import groupby

from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.iwp_website.controllers.investor_form import InvestorForm
from odoo.addons.iwp_website.controllers.investor_form import InvestorCompanyForm
from odoo.http import request
from odoo.tools.translate import _

# TODO: Try to not give sudo object to a view.


def monetary_to_text(value, currency=None):
    if currency is None:
        currency = (
            request.env['res.company']._company_default_get().currency_id
        )
    value_to_html = request.env['ir.qweb.field.monetary'].value_to_html
    html_val = value_to_html(float(value), {"display_currency": currency})
    raw_val = (
        html_val
        .replace('<span class="oe_currency_value">', "")
        .replace("</span>", "")
    )
    return raw_val


class InvestorPortal(CustomerPortal):

    @http.route(['/my/wallet/share'], type='http', auth="user", website=True)
    def my_wallet_share(self, **kw):
        """Wallet of share owned by the connected user."""
        values = self._prepare_portal_layout_values()
        shareline_mgr = request.env['share.line']

        # Share lines owned by an investor
        sharelines = shareline_mgr.sudo().search(self.shareline_domain)

        # Data structure
        # [
        #    {
        #         'structure': structure_id,
        #         'buy_url': "/struct/xx/subscription"
        #         'sell_url': "/struct/xx/sell"
        #         'total_amount': sum_of_total_amount_line,
        #         'lines': recordset('share.line'),
        #     },
        #     {
        #         ...
        #     },
        # ]
        data = []
        # Create data structure
        sharelines = sharelines.sorted(key=lambda r: r.structure.name)
        grouped_sl = groupby(sharelines, lambda r: r.structure)
        for (structure, shares) in grouped_sl:
            item = {}
            item['structure'] = structure
            item['lines'] = shareline_mgr  # New empty recordset
            item['buy_url'] = "/struct/%d/subscription" % (structure.id,)
            item['sell_url'] = "/struct/%d/sell" % (structure.id,)
            item['total_amount'] = 0
            for share in shares:
                item['total_amount'] += share.total_amount_line
                item['lines'] += share
            item['lines'] = item['lines'].sorted(
                key=lambda r: r.sudo().effective_date,
                reverse=True,
            )
            item['lines'] = item['lines'].sudo()
            data.append(item)

        # Manual share suppression
        values["back_from_delete_share"] = False
        if "delete_share_success" in request.session:
            values["back_from_delete_share"] = True
            values["delete_share_success"] = request.session[
                "delete_share_success"
            ]
            del request.session["delete_share_success"]

        values.update({
            'finproducts': data,
            'page_name': 'share_wallet',
            'default_url': '/my/wallet/share',
            'currency': (
                request.env['res.company']._company_default_get().currency_id
            ),
        })
        return request.render(
            'iwp_website.portal_my_wallet_share',
            values
        )

    @http.route('/my/history/share', type='http', auth="public", website=True)
    def my_history_share(self, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        register_mgr = request.env['subscription.register']
        sub_req_mgr = request.env['subscription.request']

        searchbar_sortings = {
            'name': {'label': _('Structure Name'), 'order': ''},
            'date': {'label': _('Date'), 'order': 'date'},
        }

        # default sortby order
        # Order by name is done after the query
        if not sortby:
            sortby = 'date'
        sort_order = 'date desc'  # Always order by date

        registers = register_mgr.sudo().search(
            self.subscription_register_domain,
            order=sort_order,
        )
        subreqs = sub_req_mgr.sudo().search(
            self.subscription_request_domain,
            order='date desc',
        )

        if sortby == 'name':
            registers = registers.sorted(
                key=lambda r: r.structure.name if r.structure.name else ''
            )
            subreqs = subreqs.sorted(
                key=lambda r: r.structure.name if r.structure.name else ''
            )

        values.update({
            'registers': registers.sudo(),
            'subreqs': subreqs.sudo(),
            'page_name': 'share_history',
            'default_url': '/my/history/share',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render(
            'iwp_website.portal_my_history_share',
            values
        )

    @http.route(['/my/wallet/loan'], type='http', auth="user", website=True)
    def my_wallet_loan(self, sortby=None, **kw):
        """Wallet of loan owned by the connected user."""
        values = self._prepare_portal_layout_values()
        loanline_mgr = request.env['loan.issue.line']

        # Order by
        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'date desc'},
            'state': {'label': _('State'), 'order': 'state'},
            'struct': {'label': _('Structure Name'), 'order': 'date desc'},
        }
        if not sortby:
            sortby = 'struct'
        sort_order = searchbar_sortings[sortby]['order']

        # Loan issue lines owned by an investor
        issuelines = loanline_mgr.sudo().search(
            self.loan_issue_line_domain, order=sort_order,
        )

        if sortby == 'struct':
            issuelines = issuelines.sorted(key=lambda r: r.structure.name)

        values.update({
            'finproducts': issuelines,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'page_name': 'loan_wallet',
            'default_url': '/my/wallet/loan',
        })
        return request.render(
            'iwp_website.portal_my_wallet_loan',
            values
        )

    @http.route('/structure', type='http', auth="public", website=True)
    def structures(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        struct_mgr = request.env['res.partner']

        searchbar_sortings = {
            'name': {'label': _('Name'), 'order': 'name'},
            'type': {'label': _('Type'), 'order': 'structure_type'},
        }

        # default sortby order
        if not sortby:
            sortby = 'name'
        sort_order = searchbar_sortings[sortby]['order']

        # count for pager
        struct_count = struct_mgr.sudo().search_count(self.structure_domain)
        # make pager
        pager = portal_pager(
            url='/structure',
            url_args={
                'sortby': sortby
            },
            total=struct_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        structures = struct_mgr.sudo().search(
            self.structure_domain,
            order=sort_order,
            limit=self._items_per_page,
            offset=pager['offset']
        )

        values.update({
            'structures': structures.sudo(),
            'page_name': 'structures',
            'pager': pager,
            'default_url': '/structure',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render(
            'iwp_website.structures',
            values
        )

    @http.route()
    def account(self, redirect=None, **post):
        """Form processing to edit user details"""
        user = request.env.user
        if user.is_company:
            form = InvestorCompanyForm()
        else:
            form = InvestorForm()
        # Prepare the form
        form.normalize_form_data(request.params)
        form.validate_form(request.params)
        form.init_form_data(request.params)
        form.set_form_defaults(request.params, user=user)
        if 'firstname' in request.params or 'lastname' in request.params:
            request.params['name'] = form.generate_name_field(
                request.params.get('firstname', ''),
                request.params.get('lastname', ''),
            )
        # Process the form
        if ('error' not in request.params
                and request.httprequest.method == 'POST'):
            if user.is_company:
                # company
                values = {
                    key: request.params[key]
                    for key in request.params
                    if key in form.company_fields
                }
                user.write(values)
                # representative
                values = {
                    key[4:]: request.params[key]
                    for key in request.params
                    if key in form.representative_fields
                }
                representative = user.child_ids[0]
                representative.write(values)
            else:
                values = {
                    key: request.params[key]
                    for key in request.params
                    if key in form.user_fields
                }
                user.write(values)
            return request.redirect('/my/home')

        qcontext = request.params
        qcontext.update({
            'page_name': 'my_details',
        })
        if user.partner_id.is_company:
            return request.render(
                'iwp_website.investor_company_details',
                qcontext
            )
        return request.render(
            'iwp_website.investor_details',
            qcontext
        )

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        # Shares
        shareline_mgr = request.env['share.line']
        shareline_count = (
            shareline_mgr.sudo().search_count(self.shareline_domain)
        )
        share_amount = sum(
            r.total_amount_line
            for r in shareline_mgr.sudo().search(self.shareline_domain)
        )
        # Loans
        loanline_mgr = request.env['loan.issue.line']
        loan_domain = self.loan_issue_line_domain
        loan_domain += [("state", "=", "waiting"), ("state", "=", "paid")]
        loanline_count = (
            loanline_mgr.sudo().search_count(self.loan_issue_line_domain)
        )
        loanline_amount = sum(
            r.amount
            for r in loanline_mgr.sudo().search(self.loan_issue_line_domain)
        )
        # Subscription request
        register_mgr = request.env['subscription.register']
        subreg_count = (
            register_mgr.sudo()
            .search_count(self.subscription_register_domain)
        )
        values.update({
            'share_count': shareline_count,
            'share_amount': share_amount,
            'loan_count': loanline_count,
            'loan_amount': loanline_amount,
            'share_history_count': subreg_count,
            'monetary_to_text': monetary_to_text,
        })
        return values

    @property
    def shareline_domain(self):
        partner = request.env.user.partner_id
        domain = [
            ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
        ]
        return domain

    @property
    def loan_issue_line_domain(self):
        partner = request.env.user.partner_id
        domain = [
            ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
        ]
        return domain

    @property
    def structure_domain(self):
        domain = [
            ('is_platform_structure', '=', True)
        ]
        return domain

    @property
    def subscription_register_domain(self):
        partner = request.env.user.partner_id
        domain = [
            '|',
            ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
            ('partner_id_to', 'child_of', [partner.commercial_partner_id.id]),
        ]
        return domain

    @property
    def subscription_request_domain(self):
        partner = request.env.user.partner_id
        domain = [
            ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
            ('state', '!=', 'paid'),
        ]
        return domain
