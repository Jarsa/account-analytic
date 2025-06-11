
def migrate(cr, version):
    cr.execute("DELETE FROM ir_ui_view WHERE name = 'stock.picking.form' AND arch_fs = 'stock_analytic/views/stock_move_views.xml';")
