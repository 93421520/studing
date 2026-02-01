# libs package compatibility wrapper
# Expose DBManager at package level regardless of underlying filename/casing
try:
    from .database import DBManager
except Exception:
    try:
        from .Database import Database as DBManager
    except Exception:
        DBManager = None