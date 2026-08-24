# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Analytic Auto Assign Distribution Template",
    "summary": "Reusable percentage-split analytic distribution templates",
    "version": "19.0.1.0.0",
    "author": "Odoo Community Association (OCA)",
    "category": "Accounting/Accounting",
    "website": "https://github.com/OCA/account-analytic",
    "license": "AGPL-3",
    "depends": [
        "account_analytic_auto_assign",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_analytic_distribution_template_views.xml",
        "views/account_move_line_views.xml",
    ],
    "installable": True,
    "application": False,
}
