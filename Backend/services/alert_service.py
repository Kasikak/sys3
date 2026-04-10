from models import db, Alert, Item, Promotion


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

        # Block resolve if the item stock is still low or out
        if alert.alertType in ('low_stock', 'out_of_stock', 'promo_low_stock'):
            item = Item.query.get(alert.ItemName)
            if item:
                if item.Stock == 0:
                    return False, f'{item.ItemName} is still out of stock. Update stock before resolving.'
                if item.Stock <= item.reorderThreshold:
                    return False, f'{item.ItemName} still has low stock ({item.Stock} units, threshold {item.reorderThreshold}). Update stock before resolving.'

        alert.status = 'dismissed'
        db.session.commit()
        return True, None

    @staticmethod
    def create_if_needed(item):
        """Create a low stock alert for an item if one doesn't already exist.
        If the item has an active promotion, uses 'promo_low_stock' type instead."""
        if item.Stock > item.reorderThreshold:
            return

        # Check if there is already any active alert for this item
        existing = Alert.query.filter_by(ItemName=item.ItemName, status='active').first()
        if existing:
            return

        # Determine alert type — check for active promotion
        promo = Promotion.query.filter_by(ItemName=item.ItemName, isActive=True).first()

        if item.Stock == 0:
            alert_type = 'out_of_stock'
            message    = f'{item.ItemName} is out of stock'
        elif promo:
            alert_type = 'promo_low_stock'
            message    = f'{item.ItemName} is low on stock ({item.Stock} units left). Promotion: {promo.promotionName}'
        else:
            alert_type = 'low_stock'
            message    = f'{item.ItemName} is low on stock ({item.Stock} units left)'

        db.session.add(Alert(
            ItemName=item.ItemName,
            alertType=alert_type,
            message=message,
            status='active'
        ))
        db.session.commit()
