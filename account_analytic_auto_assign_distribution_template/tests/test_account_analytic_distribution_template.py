# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestAccountAnalyticDistributionTemplate(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
