# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import Command
from odoo.tests import common


class TestPurchaseProcurementAnalytic(common.TransactionCase):
    """Use case : Prepare some data for current test case"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # Group all the RFQs of the vendor: by default ("On Order") Odoo
        # already creates one RFQ per sale order for MTO needs.
        cls.vendor = cls.env["res.partner"].create(
            {"name": "Partner #2", "group_rfq": "all"}
        )
        mto = cls.env.ref("stock.route_warehouse0_mto")
        mto.write({"active": True, "product_selectable": True})
        buy = cls.env.ref("purchase_stock.route_warehouse0_buy")
        buy.product_selectable = True
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "is_storable": True,
                "seller_ids": [Command.create({"partner_id": cls.vendor.id})],
                "route_ids": [Command.set([buy.id, mto.id])],
            }
        )
        cls.service_product = cls.env["product.product"].create(
            {
                "name": "Product Service Test",
                "type": "service",
                "service_tracking": "subcontract",
                "seller_ids": [Command.create({"partner_id": cls.vendor.id})],
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Partner #1"})
        plan = cls.env.ref("analytic.analytic_plan_projects")
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {"name": "Test Analytic Account", "plan_id": plan.id}
        )
        cls.analytic_account_2 = cls.env["account.analytic.account"].create(
            {"name": "Test Analytic Account 2", "plan_id": plan.id}
        )

    def _create_sale(self, product, distributions):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom_qty": 1,
                            "analytic_distribution": distribution,
                        }
                    )
                    for distribution in distributions
                ],
            }
        )
        sale_order.action_confirm()
        return sale_order

    def _po_lines(self, product):
        return self.env["purchase.order.line"].search([("product_id", "=", product.id)])

    def _distribution(self, account, percent=100.0):
        return {str(account.id): percent}

    def test_sale_to_procurement(self):
        distribution = self._distribution(self.analytic_account)
        self._create_sale(self.product, [distribution])
        po_line = self._po_lines(self.product)
        self.assertEqual(len(po_line), 1)
        self.assertEqual(po_line.analytic_distribution, distribution)

    def test_sale_service_product(self):
        distribution = self._distribution(self.analytic_account)
        self._create_sale(self.service_product, [distribution])
        po_line = self._po_lines(self.service_product)
        self.assertEqual(len(po_line), 1)
        self.assertEqual(po_line.analytic_distribution, distribution)

    def test_same_distribution_grouped(self):
        distribution = self._distribution(self.analytic_account)
        self._create_sale(self.product, [distribution])
        self._create_sale(self.product, [distribution])
        po_lines = self._po_lines(self.product)
        self.assertEqual(len(po_lines.order_id), 1)
        self.assertEqual(sum(po_lines.mapped("product_qty")), 2)
        self.assertEqual(
            po_lines.mapped("analytic_distribution"), [distribution] * len(po_lines)
        )

    def test_no_distribution(self):
        self._create_sale(self.product, [False])
        self._create_sale(self.product, [self._distribution(self.analytic_account)])
        po_lines = self._po_lines(self.product)
        self.assertEqual(len(po_lines.order_id), 2)
        self.assertFalse(
            po_lines.filtered(lambda line: not line.analytic_distribution).order_id
            & po_lines.filtered("analytic_distribution").order_id
        )

    def test_different_distribution_split(self):
        distribution_1 = self._distribution(self.analytic_account)
        distribution_2 = self._distribution(self.analytic_account_2)
        self._create_sale(self.product, [distribution_1])
        self._create_sale(self.product, [distribution_2])
        po_lines = self._po_lines(self.product)
        self.assertEqual(len(po_lines), 2)
        self.assertEqual(len(po_lines.order_id), 2)
        self.assertCountEqual(
            po_lines.mapped("analytic_distribution"),
            [distribution_1, distribution_2],
        )

    def test_different_distribution_same_sale(self):
        distribution_1 = self._distribution(self.analytic_account)
        distribution_2 = {
            str(self.analytic_account.id): 50.0,
            str(self.analytic_account_2.id): 50.0,
        }
        self._create_sale(self.product, [distribution_1, distribution_2])
        po_lines = self._po_lines(self.product)
        self.assertEqual(len(po_lines), 2)
        self.assertCountEqual(
            po_lines.mapped("analytic_distribution"),
            [distribution_1, distribution_2],
        )

    def test_different_distribution_same_sale_default_grouping(self):
        """With the default "On Order" grouping Odoo merges the lines of one
        sale order into a single PO line, keeping only one distribution."""
        self.vendor.group_rfq = "default"
        distribution_1 = self._distribution(self.analytic_account)
        distribution_2 = self._distribution(self.analytic_account_2)
        self._create_sale(self.product, [distribution_1, distribution_2])
        po_lines = self._po_lines(self.product)
        self.assertEqual(len(po_lines), 2)
        self.assertCountEqual(
            po_lines.mapped("analytic_distribution"),
            [distribution_1, distribution_2],
        )

    def _test_multi_step(self, delivery_steps):
        self.env.ref("stock.warehouse0").delivery_steps = delivery_steps
        distribution_1 = self._distribution(self.analytic_account)
        distribution_2 = self._distribution(self.analytic_account_2)
        self._create_sale(self.product, [distribution_1])
        self._create_sale(self.product, [distribution_2])
        self._create_sale(self.product, [distribution_1])
        po_lines = self._po_lines(self.product)
        self.assertEqual(len(po_lines.order_id), 2)
        for distribution, qty in ((distribution_1, 2), (distribution_2, 1)):
            line = po_lines.filtered(
                lambda line, dist=distribution: line.analytic_distribution == dist
            )
            self.assertEqual(sum(line.mapped("product_qty")), qty)

    def test_pick_ship(self):
        self._test_multi_step("pick_ship")

    def test_pick_pack_ship(self):
        self._test_multi_step("pick_pack_ship")

    def test_search_key(self):
        distribution = self._distribution(self.analytic_account)
        self._create_sale(self.product, [distribution])
        po = self._po_lines(self.product).order_id
        PurchaseOrder = self.env["purchase.order"]
        key = json.dumps({str(self.analytic_account.id): 100.0})
        self.assertEqual(
            PurchaseOrder.search([("mto_analytic_distribution_key", "=", key)]), po
        )
        other_key = json.dumps({str(self.analytic_account_2.id): 100.0})
        self.assertFalse(
            PurchaseOrder.search([("mto_analytic_distribution_key", "=", other_key)])
        )
