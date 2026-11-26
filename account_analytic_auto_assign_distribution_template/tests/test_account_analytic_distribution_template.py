# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountAnalyticDistributionTemplate(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.group_ids |= cls.env.ref("analytic.group_analytic_accounting")
        cls.plan_admin = cls.env["account.analytic.plan"].create(
            {"name": "Admin Plan Test"}
        )
        cls.account_admin = cls.env["account.analytic.account"].create(
            {"name": "Administration Test", "plan_id": cls.plan_admin.id}
        )
        cls.account_ops = cls.env["account.analytic.account"].create(
            {"name": "Operations Test", "plan_id": cls.plan_admin.id}
        )
        cls.template = cls.env["account.analytic.distribution.template"].create(
            {
                "name": "60/40 Admin-Ops Test",
                "analytic_distribution": {
                    str(cls.account_admin.id): 60.0,
                    str(cls.account_ops.id): 40.0,
                },
            }
        )
        cls.account_expense = cls.env["account.account"].search(
            [("account_type", "=", "expense")], limit=1
        )
        cls.account_payable = cls.env["account.account"].search(
            [("account_type", "=", "liability_payable")], limit=1
        )

    def test_onchange_applies_template_distribution(self):
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "line_ids": [
                    Command.create(
                        {
                            "name": "Shared cost",
                            "account_id": self.account_expense.id,
                            "debit": 100.0,
                            "credit": 0.0,
                        }
                    ),
                    Command.create(
                        {
                            "name": "Counterpart",
                            "account_id": self.account_payable.id,
                            "debit": 0.0,
                            "credit": 100.0,
                        }
                    ),
                ],
            }
        )
        line = move.line_ids[0]
        line.distribution_template_id = self.template
        line._onchange_distribution_template_id()
        self.assertEqual(
            line.analytic_distribution,
            {
                str(self.account_admin.id): 60.0,
                str(self.account_ops.id): 40.0,
            },
        )

    def test_multi_company(self):
        company_b = self.setup_other_company()["company"]
        template_b = self.env["account.analytic.distribution.template"].create(
            {"name": "Company B Test", "company_id": company_b.id}
        )
        shared = self.env["account.analytic.distribution.template"].create(
            {"name": "Shared Test", "company_id": False}
        )
        user = self.env["res.users"].create(
            {
                "name": "Template User Test",
                "login": "template_user_test",
                "company_id": self.env.company.id,
                "company_ids": [Command.set(self.env.company.ids)],
                "group_ids": [
                    Command.set(
                        [
                            self.env.ref("account.group_account_invoice").id,
                            self.env.ref("analytic.group_analytic_accounting").id,
                        ]
                    )
                ],
            }
        )
        visible = (
            self.env["account.analytic.distribution.template"]
            .with_user(user)
            .search([("id", "in", (self.template | template_b | shared).ids)])
        )
        self.assertEqual(visible, self.template | shared)
        line = self.init_invoice("in_invoice", products=self.product_a).invoice_line_ids
        with self.assertRaises(UserError):
            line.distribution_template_id = template_b
