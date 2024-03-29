# Copyright 2013-2018 Open Architects Consulting SPRL.
# Copyright 2018-Coop IT Easy SC (<http://www.coopiteasy.be>)
# - Houssine BAKKALI - <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).#


{
    "name": "Investor Wallet Platform Base",
    "version": "12.0.1.7.0",
    "depends": [
        "cooperator",
        "easy_my_coop_loan",
        "partner_changeset",
        "l10n_be_cooperator_national_number",
    ],
    "author": "Coop IT Easy SC",
    "category": "Cooperative management",
    "website": "https://coopiteasy.be",
    "license": "AGPL-3",
    "summary": """
    This module add a layer on top of easy my coop to allow handling several
    structures to rise capital through the easy my coop flow.
    """,
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "security/iwp_security.xml",
        "data/sector_area_data.xml",
        "views/res_partner_view.xml",
        "views/operation_request_view.xml",
        "views/subscription_request_view.xml",
        "views/invoice_view.xml",
        "views/res_users_view.xml",
        "views/product_view.xml",
        "views/activity_area_view.xml",
        "views/loan_issue_view.xml",
        "views/res_company_view.xml",
        "views/ir_mail_server_view.xml",
        "views/mail_template.xml",
        "views/menus.xml",
        "report/report_templates.xml",
        "report/cooperator_certificat.xml",
        "report/cooperator_to_certificat.xml",
        "report/easy_my_coop_report.xml",
        "report/cooperator_invoice.xml",
        "data/cron.xml",
        "data/mail_template_data.xml",
    ],
    "demo": [
        "demo/account.xml",
        "demo/structure.xml",
        "demo/mail_template_demo.xml",
        "demo/coop.xml",
        "demo/users.xml",
    ],
    "installable": True,
    "application": True,
}
