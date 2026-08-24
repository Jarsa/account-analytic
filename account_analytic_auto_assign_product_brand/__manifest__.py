# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Analytic Auto Assign Product Brand",
    "summary": "Automatically assign analytic accounts based on the product brand",
    "version": "19.0.1.0.0",
    "author": "Odoo Community Association (OCA)",
    "category": "Accounting/Accounting",
    "website": "https://github.com/OCA/account-analytic",
    "license": "AGPL-3",
    "depends": [
        "account_analytic_auto_assign",
        "product_brand",
        "sale",
        "purchase",
        "hr_expense",
    ],
    "data": [
        "views/product_brand_views.xml",
    ],
    "installable": True,
    "application": False,
}
