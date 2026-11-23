Since version 20.0, Odoo itself copies the analytic distribution of a sale
order line to the purchase order line created by a *Replenish on Order (MTO)*
procurement. However, when several purchase needs are grouped, Odoo merges
them into the same purchase order line and keeps only one analytic
distribution, so part of the cost ends up on the wrong analytic account.

This module keeps purchase needs with different analytic distributions apart:

- they are never merged into the same purchase order line, and
- they go to different requests for quotation, even when the vendor groups
  its RFQs (*Group RFQ* = *Always*, *Daily* or *Weekly*).
