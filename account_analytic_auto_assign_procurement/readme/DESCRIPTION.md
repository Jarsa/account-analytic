Purchase orders created from a sale order (make to order, buy route) take
the **Project** of the sale order (see `account_analytic_auto_assign_sale`)
and, when the operating unit modules are installed, its operating unit.

Purchase orders are only grouped with procurements of the same project, so
one RFQ never mixes the purchases of two projects, even with the vendor set
to group RFQs by day, week or all.

It replaces `procurement_mto_analytic`: the analytic distribution of the
sale line already reaches the purchase line in standard Odoo.
