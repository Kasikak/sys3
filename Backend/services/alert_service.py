from models import db, Alert, Item


class AlertService:

    @staticmethod
    def get_all(resolved=False):
        status = 'dismissed' if resolved else 'active'
        return Alert.query.filter_by(status=status).order_by(Alert.createdAt.desc()).all()

    @staticmethod
    def resolve(alert_id):
        alert = Alert.query.get(alert_id)
        if not alert:
            return False, 'Alert not found'
        alert.status = 'dismissed'
        db.session.commit()
        return True, None

    @staticmethod
    def create_if_needed(item):
        """Create a low stock alert for an item if one doesn't already exist."""
        if item.Stock <= item.reorderThreshold:
            existing = Alert.query.filter_by(ItemName=item.ItemName, status='active').first()
            if not existing:
                alert_type = 'low_stock' if item.Stock > 0 else 'out_of_stock'
                message    = f'"{item.ItemName}" is low on stock ({item.Stock} remaining)'
                db.session.add(Alert(
                    ItemName=item.ItemName,
                    alertType=alert_type,
                    message=message,
                    status='active'
                ))
