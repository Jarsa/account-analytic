# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Analytic Auto Assign Operating Unit",
    "summary": "Automatically assign analytic accounts based on the operating unit",
    "version": "19.0.1.0.0",
    "author": "Odoo Community Association (OCA)",
    "category": "Accounting/Accounting",
    "website": "https://github.com/OCA/account-analytic",
    "license": "AGPL-3",
    "depends": [
        "account_analytic_auto_assign",
        "account_operating_unit",
        "sale_operating_unit",
    ],
    "data": [
        "views/operating_unit_views.xml",
    ],
    "installable": True,
    "application": False,
}
