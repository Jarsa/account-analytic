# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Analytic Auto Assign Procurement",
    "summary": "Purchase orders created from sales take the project of the"
    " sale and are grouped by project",
    "version": "19.0.1.0.0",
    "author": "Odoo Community Association (OCA)",
    "category": "Accounting/Accounting",
    "website": "https://github.com/OCA/account-analytic",
    "license": "AGPL-3",
    "depends": [
        "account_analytic_auto_assign_purchase",
        "account_analytic_auto_assign_sale",
        "sale_purchase_stock",
    ],
    "installable": True,
    "application": False,
}
