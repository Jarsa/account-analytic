# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Analytic Auto Assign Product Category",
    "summary": "Require an analytic account on each product category",
    "version": "19.0.1.0.0",
    "author": "Odoo Community Association (OCA)",
    "category": "Accounting/Accounting",
    "website": "https://github.com/OCA/account-analytic",
    "license": "AGPL-3",
    "depends": [
        "account_analytic_auto_assign",
        "product",
    ],
    "data": [
        "views/product_category_views.xml",
    ],
    "installable": True,
    "application": False,
}
