from models import db, Sale, SaleItem, Item
from services.alert_service import AlertService


class SaleService:

    @staticmethod
    def get_all(limit=50):
        return Sale.query.order_by(Sale.date.desc()).limit(limit).all()

    @staticmethod
    def record(items_data, payment_method, cashier_id):
        """
        items_data: list of dicts with keys product_id, quantity, price
        Returns (sale, error)
        """
        subtotal = 0.0
        to_sell  = []

        for entry in items_data:
            item = Item.query.filter_by(ItemName=entry['product_id']).first()
            if not item:
                return None, f'Item "{entry["product_id"]}" not found'
            if item.Stock < entry['quantity']:
                return None, f'Insufficient stock for "{item.ItemName}"'
            subtotal += item.Price * entry['quantity']
            to_sell.append((item, entry['quantity']))

        total = round(subtotal, 2)
        sale  = Sale(cashierID=cashier_id, total=total, tax=0.0, payment_method=payment_method)
        db.session.add(sale)
        db.session.flush()

        for item, qty in to_sell:
            db.session.add(SaleItem(
                transactionID=sale.transactionID,
                ItemName=item.ItemName,
                quantity=qty,
                priceAtSale=item.Price
            ))
            item.Stock -= qty
            AlertService.create_if_needed(item)

        db.session.commit()
        return sale, None
