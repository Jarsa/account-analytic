# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountAnalyticAutoAssignOperatingUnit(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.group_ids |= (
            cls.env.ref("operating_unit.group_manager_operating_unit")
            | cls.env.ref("operating_unit.group_multi_operating_unit")
            | cls.env.ref("sales_team.group_sale_manager")
        )
        plan = cls.env["account.analytic.plan"].create({"name": "Branch Plan Test"})
        cls.account_a, cls.account_b = cls.env["account.analytic.account"].create(
            [
                {"name": "Branch A", "plan_id": plan.id},
                {"name": "Branch B", "plan_id": plan.id},
            ]
        )
        cls.unit_a, cls.unit_b = cls.env["operating.unit"].create(
            [
                {
                    "name": f"OU {code}",
                    "code": f"OU{code}",
                    "company_id": cls.env.company.id,
                    "partner_id": cls.env.company.partner_id.id,
                }
                for code in "AB"
            ]
        )
        cls.env.user.operating_unit_ids |= cls.unit_a | cls.unit_b
        cls.env["account.analytic.distribution.model"].create(
            [
                {
                    "operating_unit_id": cls.unit_a.id,
                    "analytic_distribution": {str(cls.account_a.id): 100.0},
                },
                {
                    "operating_unit_id": cls.unit_b.id,
                    "analytic_distribution": {str(cls.account_b.id): 100.0},
                },
            ]
        )

    def _order_vals(self, unit):
        return {
            "partner_id": self.partner_a.id,
            "operating_unit_id": unit.id,
            "order_line": [Command.create({"product_id": self.product_a.id})],
        }

    def test_invoice_line(self):
        invoice = self.init_invoice("out_invoice", products=self.product_a)
        invoice.write(
            {
                "operating_unit_id": self.unit_b.id,
                "line_ids": [
                    Command.update(line.id, {"operating_unit_id": self.unit_b.id})
                    for line in invoice.line_ids
                ],
            }
        )
        self.assertEqual(
            invoice.invoice_line_ids.analytic_distribution,
            {str(self.account_b.id): 100.0},
        )

    def test_sale_line(self):
        order = self.env["sale.order"].create(self._order_vals(self.unit_a))
        self.assertEqual(
            order.order_line.analytic_distribution, {str(self.account_a.id): 100.0}
        )
        order.operating_unit_id = self.unit_b
        self.assertEqual(
            order.order_line.analytic_distribution, {str(self.account_b.id): 100.0}
        )

    def test_without_operating_unit_criterion(self):
        distribution = self.env[
            "account.analytic.distribution.model"
        ]._get_distribution({"company_id": self.env.company.id})
        self.assertFalse(distribution)
