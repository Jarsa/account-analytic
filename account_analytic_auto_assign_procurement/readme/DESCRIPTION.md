Purchase orders created from a sale order (make to order, buy route) take
the analytic account of the sale order (see
`account_analytic_auto_assign_sale`). The operating unit of the sale is
passed by `account_analytic_auto_assign_procurement_operating_unit`.

Purchase orders are only grouped with procurements of the same analytic account,
so one RFQ never mixes the purchases of two projects, even with the vendor set
to group RFQs by day, week or all.

It replaces `procurement_mto_analytic`: the analytic distribution of the
sale line already reaches the purchase line in standard Odoo.
