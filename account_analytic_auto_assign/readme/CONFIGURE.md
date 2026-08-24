This module has no screen of its own to configure rules manually — it is
meant to be driven entirely by other modules (product category, brand,
operating unit, project, distribution templates...) that each add their
own required field on the source they represent, and create/update the
matching `account.analytic.auto.assign.rule` record automatically.

If the native Odoo engine is preferred instead, just create rules in
Accounting > Configuration > Analytic > Analytic Distribution Models: as
soon as one record exists there, this module stops interfering.
