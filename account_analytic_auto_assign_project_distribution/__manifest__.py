# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Analytic Auto Assign Project Distribution",
    "summary": "Predefined analytic distribution on the project, applied"
    " wherever the project is set",
    "version": "19.0.1.0.0",
    "author": "Odoo Community Association (OCA)",
    "category": "Accounting/Accounting",
    "website": "https://github.com/OCA/account-analytic",
    "license": "AGPL-3",
    "depends": [
        "account_analytic_auto_assign_account_move",
    ],
    "data": [
        "views/account_analytic_account_views.xml",
    ],
    "installable": True,
    "application": False,
}
