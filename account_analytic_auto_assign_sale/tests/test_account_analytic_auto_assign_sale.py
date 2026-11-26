# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountAnalyticAutoAssignSale(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.group_ids |= cls.env.ref("sales_team.group_sale_manager")
        cls.plan = cls.env["account.analytic.plan"].create(
            {"name": "Project Plan Test"}
        )
        cls.project_account = cls.env["account.analytic.account"].create(
            {"name": "Project Test", "plan_id": cls.plan.id}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Project Partner Test"})
        cls.product = cls.env["product.product"].create(
            {"name": "Project Product Test"}
        )

    def test_project_inherited_by_lines(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "analytic_account_id": self.project_account.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product.id, "product_uom_qty": 1}
                    )
                ],
            }
        )
        self.assertEqual(
            order.order_line.analytic_distribution,
            {str(self.project_account.id): 100.0},
        )

    def test_project_carried_over_to_invoice(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "analytic_account_id": self.project_account.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product.id, "product_uom_qty": 1}
                    )
                ],
            }
        )
        order.action_confirm()
        invoice = order._create_invoices()
        self.assertEqual(invoice.analytic_account_id, self.project_account)
        line = invoice.invoice_line_ids.filtered(
            lambda line: line.display_type == "product"
        )
        self.assertEqual(
            line.analytic_distribution, {str(self.project_account.id): 100.0}
        )

    def test_no_project_leaves_distribution_untouched(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product.id, "product_uom_qty": 1}
                    )
                ],
            }
        )
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
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "analytic_account_id": self.project_account.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product.id, "product_uom_qty": 1}
                    )
                ],
            }
        )
        ((key, percentage),) = order.order_line.analytic_distribution.items()
        self.assertEqual(
            set(key.split(",")), {str(self.project_account.id), str(branch.id)}
        )
        self.assertEqual(percentage, 100.0)

    def _services_order(self, analytic_account=False):
        product = self.env["product.product"].create(
            {
                "name": "Reinvoiced Service Test",
                "type": "service",
                "list_price": 110,
                "reinvoice_policy": "sales_price",
                "invoice_policy": "delivery",
            }
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "analytic_account_id": analytic_account and analytic_account.id,
                "order_line": [Command.create({"product_id": product.id})],
            }
        )
        order.action_confirm()
        self.env["account.analytic.line"].with_context(
            from_services_and_material=True
        ).create(
            {
                "name": "Services & Materials Test",
                "product_id": product.id,
                "unit_amount": 1,
                "order_id": order.id,
            }
        )
        return order

    def test_services_and_materials_account_inherited(self):
        """The account created by the Services & Materials flow is the native
        analytic account of the order, so lines and invoices carry it."""
        order = self._services_order()
        account = order.analytic_account_id
        self.assertTrue(account)
        self.assertEqual(
            order.order_line.analytic_distribution, {str(account.id): 100.0}
        )
        invoice = order._create_invoices()
        self.assertEqual(invoice.analytic_account_id, account)
        self.assertEqual(
            invoice.invoice_line_ids.analytic_distribution, {str(account.id): 100.0}
        )

    def test_services_and_materials_keeps_captured_account(self):
        order = self._services_order(self.project_account)
        self.assertEqual(order.analytic_account_id, self.project_account)
        self.assertEqual(
            order.order_line.analytic_distribution,
            {str(self.project_account.id): 100.0},
        )
        self.assertEqual(
            order._create_invoices().analytic_account_id, self.project_account
        )
