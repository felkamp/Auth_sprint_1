from src.db.postgres import db
from datetime import datetime


class AuditMixin:
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now)
    update_at = db.Column(db.DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
