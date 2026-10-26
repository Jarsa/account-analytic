# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountAnalyticAutoAssignPurchase(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.plan = cls.env["account.analytic.plan"].create(
            {"name": "Purchase Project Plan Test"}
        )
        cls.project_account = cls.env["account.analytic.account"].create(
            {"name": "Purchase Project Test", "plan_id": cls.plan.id}
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Purchase Project Partner Test"}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Purchase Project Product Test"}
        )

    def _create_order(self, with_project):
        return self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "analytic_account_id": self.project_account.id
                if with_project
                else False,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_qty": 1,
                            "price_unit": 10.0,
                            "name": self.product.name,
                            "date_planned": "2026-01-01",
                        }
                    )
                ],
            }
        )

    def test_project_inherited_by_lines(self):
        order = self._create_order(with_project=True)
        self.assertEqual(
            order.order_line.analytic_distribution,
            {str(self.project_account.id): 100.0},
        )

    def test_project_carried_over_to_bill(self):
        order = self._create_order(with_project=True)
        order.button_confirm()
        bill = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner.id,
                "purchase_id": order.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 10.0,
                            "purchase_line_id": order.order_line.id,
                        }
                    )
                ],
            }
        )
        line = bill.invoice_line_ids.filtered(
            lambda line: line.display_type == "product"
        )
        self.assertEqual(
            line.analytic_distribution, {str(self.project_account.id): 100.0}
        )

    def test_no_project_leaves_distribution_untouched(self):
        order = self._create_order(with_project=False)
        self.assertFalse(order.order_line.analytic_distribution)

    def test_project_merged_with_distribution_model(self):
        branch_plan = self.env["account.analytic.plan"].create({"name": "Branch"})
        branch = self.env["account.analytic.account"].create(
            {"name": "Branch", "plan_id": branch_plan.id}
        )
        self.env["account.analytic.distribution.model"].create(
            {
                "product_id": self.product.id,
                "analytic_distribution": {str(branch.id): 100.0},
            }
        )
        order = self._create_order(with_project=True)
        ((key, percentage),) = order.order_line.analytic_distribution.items()
        self.assertEqual(
            set(key.split(",")), {str(self.project_account.id), str(branch.id)}
        )
        self.assertEqual(percentage, 100.0)

    def test_bill_from_order_has_project(self):
        self.product.purchase_method = "purchase"
        order = self._create_order(with_project=True)
        order.button_confirm()
        order.action_create_invoice()
        self.assertEqual(order.invoice_ids.analytic_account_id, self.project_account)
