Extends `account_analytic_auto_assign` so its rules can also match by
**operating unit** (branch), read from `operating_unit_id` on invoice/bill
lines and on sale order lines.

Purchases are not covered: as of this writing there is no
`purchase_operating_unit` module upstream, so purchase orders have no
operating unit to read from.
