1.  Make sure the product can be bought on order: give it (or its
    category) the *Buy* and *Replenish on Order (MTO)* routes, and a
    vendor.
2.  Create a sale order with that product and set an *Analytic
    Distribution* on its lines. Use different distributions on several
    lines or sale orders.
3.  *Confirm* the sale orders.
4.  Each analytic distribution gets its own purchase order line, and its
    own request for quotation, with the same analytic distribution as the
    sale order line.
