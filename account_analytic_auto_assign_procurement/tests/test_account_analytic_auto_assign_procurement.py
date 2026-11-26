# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestAccountAnalyticAutoAssignProcurement(BaseCommon):
    # The test only checks the procurement flow, not access rights.
    _test_user_groups = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        plan = cls.env["account.analytic.plan"].create({"name": "Project Plan Test"})
        cls.project_a, cls.project_b = cls.env["account.analytic.account"].create(
            [
                {"name": "Project A", "plan_id": plan.id},
                {"name": "Project B", "plan_id": plan.id},
            ]
        )
        cls.vendor = cls.env["res.partner"].create(
            {"name": "MTO Vendor Test", "group_rfq": "all"}
        )
        cls.customer = cls.env["res.partner"].create({"name": "MTO Customer Test"})
        warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        mto_route = cls.env.ref("stock.route_warehouse0_mto")
        mto_route.active = True
        buy_route = warehouse.buy_pull_id.route_id
        # Since 20.0 the buy route is not selectable on products by default.
        buy_route.product_selectable = True
        cls.product = cls.env["product.product"].create(
            {
                "name": "MTO Product Test",
                "is_storable": True,
                "invoice_policy": "order",
                "route_ids": [Command.set([mto_route.id, buy_route.id])],
                "seller_ids": [Command.create({"partner_id": cls.vendor.id})],
            }
        )

    def _create_sale(self, project, **vals):
        return self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "analytic_account_id": project.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product.id, "product_uom_qty": 1}
                    )
                ],
                **vals,
            }
        )

    def _draft_purchases(self):
        return self.env["purchase.order"].search(
            [("partner_id", "=", self.vendor.id), ("state", "=", "draft")]
        )

    def _confirm_sale(self, project, **vals):
        self._create_sale(project, **vals).action_confirm()
        return self._draft_purchases()

    def test_rfq_takes_project_and_is_grouped_by_project(self):
        purchase_a = self._confirm_sale(self.project_a)
        self.assertEqual(purchase_a.analytic_account_id, self.project_a)
        self.assertEqual(
            purchase_a.order_line.analytic_distribution,
            {str(self.project_a.id): 100.0},
        )
        purchases = self._confirm_sale(self.project_b)
        self.assertEqual(len(purchases), 2)
        self.assertEqual((purchases - purchase_a).analytic_account_id, self.project_b)
        self.assertEqual(len(self._confirm_sale(self.project_a)), 2)

    def test_project_carried_over_to_invoice_rfq_and_bill(self):
        order = self._create_sale(self.project_a)
        order.action_confirm()
        invoice = order._create_invoices()
        self.assertEqual(invoice.analytic_account_id, self.project_a)
        self.assertEqual(
            invoice.invoice_line_ids.analytic_distribution,
            {str(self.project_a.id): 100.0},
        )
        purchase = self._draft_purchases()
        self.assertEqual(purchase.analytic_account_id, self.project_a)
        purchase.button_confirm()
        purchase.order_line.qty_received = 1
        purchase.action_create_invoice()
        bill = purchase.invoice_ids
        self.assertEqual(bill.analytic_account_id, self.project_a)
        self.assertEqual(
            bill.invoice_line_ids.analytic_distribution,
            {str(self.project_a.id): 100.0},
        )
