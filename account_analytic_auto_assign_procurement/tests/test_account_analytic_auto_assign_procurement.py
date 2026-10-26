# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestAccountAnalyticAutoAssignProcurement(BaseCommon):
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
        cls.product = cls.env["product.product"].create(
            {
                "name": "MTO Product Test",
                "is_storable": True,
                "route_ids": [
                    Command.set([mto_route.id, warehouse.buy_pull_id.route_id.id])
                ],
                "seller_ids": [Command.create({"partner_id": cls.vendor.id})],
            }
        )

    def _confirm_sale(self, project):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "analytic_account_id": project.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product.id, "product_uom_qty": 1}
                    )
                ],
            }
        )
        order.action_confirm()
        return self.env["purchase.order"].search(
            [("partner_id", "=", self.vendor.id), ("state", "=", "draft")]
        )

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
