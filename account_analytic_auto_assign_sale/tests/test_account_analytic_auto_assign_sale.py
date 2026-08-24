# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestAccountAnalyticAutoAssignSale(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
