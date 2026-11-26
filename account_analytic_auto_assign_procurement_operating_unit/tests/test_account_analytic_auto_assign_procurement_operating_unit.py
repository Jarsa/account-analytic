# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from odoo.addons.account_analytic_auto_assign_procurement.tests import (
    test_account_analytic_auto_assign_procurement as procurement_test,
)


@tagged("post_install", "-at_install")
class TestAccountAnalyticAutoAssignProcurementOperatingUnit(
    procurement_test.TestAccountAnalyticAutoAssignProcurement
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.unit = cls.env["operating.unit"].create(
            {
                "name": "OU Procurement Test",
                "code": "OUPT",
                "company_id": cls.env.company.id,
                "partner_id": cls.env.company.partner_id.id,
            }
        )
        cls.env.user.operating_unit_ids |= cls.unit

    def test_rfq_takes_operating_unit(self):
        purchase = self._confirm_sale(self.project_a, operating_unit_id=self.unit.id)
        self.assertEqual(purchase.analytic_account_id, self.project_a)
        self.assertEqual(purchase.operating_unit_id, self.unit)
        self.assertEqual(purchase.requesting_operating_unit_id, self.unit)
