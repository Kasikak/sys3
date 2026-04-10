from models import db, Promotion, Alert, Item


class PromotionService:

    @staticmethod
    def get_all():
        """Return all items with their active promotion info (if any)."""
        items = Item.query.order_by(Item.ItemName).all()
        result = []
        for item in items:
            promo = Promotion.query.filter_by(ItemName=item.ItemName, isActive=True).first()
            result.append({
                'item_name':         item.ItemName,
                'price':             item.Price,
                'stock':             item.Stock,
                'category':          item.Category,
                'reorder_threshold': item.reorderThreshold,
                'promotion': {
                    'id':               promo.promotionID,
                    'promotion_name':   promo.promotionName,
                    'reason':           promo.reason,
                    'threshold_qty':    promo.thresholdQty,
                    'discount_percent': promo.discountPercent,
                    'created_at':       promo.createdAt.isoformat(),
                    'updated_at':       promo.updatedAt.isoformat(),
                } if promo else None
            })
        return result, None

    @staticmethod
    def set_promotion(item_name, promotion_name, reason, threshold_qty, discount_percent):
        """Create or reactivate a promotion for an item."""
        item = Item.query.get(item_name)
        if not item:
            return None, 'Item not found'

        if not promotion_name or not reason:
            return None, 'Promotion name and reason are required'
        if threshold_qty is None or threshold_qty < 1:
            return None, 'Threshold quantity must be at least 1'
        if discount_percent is None or not (0 < discount_percent <= 100):
            return None, 'Discount percent must be between 0 and 100'

        existing = Promotion.query.filter_by(ItemName=item_name).first()
        if existing:
            existing.promotionName   = promotion_name
            existing.reason          = reason
            existing.thresholdQty    = threshold_qty
            existing.discountPercent = discount_percent
            existing.isActive        = True
            from datetime import datetime, timezone
            existing.updatedAt = datetime.now(timezone.utc)
        else:
            db.session.add(Promotion(
                ItemName=item_name,
                promotionName=promotion_name,
                reason=reason,
                thresholdQty=threshold_qty,
                discountPercent=discount_percent,
                isActive=True
            ))

        db.session.commit()

        # Check for promo low-stock alert immediately after setting
        PromotionService.check_promo_low_stock_alert(item_name)

        promo = Promotion.query.filter_by(ItemName=item_name, isActive=True).first()
        return {
            'id':               promo.promotionID,
            'item_name':        promo.ItemName,
            'promotion_name':   promo.promotionName,
            'reason':           promo.reason,
            'threshold_qty':    promo.thresholdQty,
            'discount_percent': promo.discountPercent,
        }, None

    @staticmethod
    def remove_promotion(item_name):
        """Deactivate a promotion for an item and dismiss any promo alerts."""
        promo = Promotion.query.filter_by(ItemName=item_name, isActive=True).first()
        if not promo:
            return False, 'No active promotion found for this item'

        promo.isActive = False
        from datetime import datetime, timezone
        promo.updatedAt = datetime.now(timezone.utc)

        # Dismiss any active promo_low_stock alerts for this item
        stale_alerts = Alert.query.filter_by(
            ItemName=item_name, alertType='promo_low_stock', status='active'
        ).all()
        for a in stale_alerts:
            a.status = 'dismissed'

        db.session.commit()
        return True, None

    @staticmethod
    def check_promo_low_stock_alert(item_name):
        """Create a promo_low_stock alert if a promotional item is running low."""
        item  = Item.query.get(item_name)
        promo = Promotion.query.filter_by(ItemName=item_name, isActive=True).first()

        if not item or not promo:
            return

        if item.Stock <= item.reorderThreshold:
            existing = Alert.query.filter_by(
                ItemName=item_name, alertType='promo_low_stock', status='active'
            ).first()
            if not existing:
                message = (
                    f'Promotional item "{item.ItemName}" is low on stock '
                    f'({item.Stock} remaining) — active promotion: "{promo.promotionName}"'
                )
                db.session.add(Alert(
                    ItemName=item_name,
                    alertType='promo_low_stock',
                    message=message,
                    status='active'
                ))
                db.session.commit()
