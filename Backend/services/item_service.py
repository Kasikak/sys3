from models import db, Item


class ItemService:

    @staticmethod
    def get_all(search='', category=''):
        q = Item.query
        if search:
            q = q.filter(Item.ItemName.ilike(f'%{search}%'))
        if category:
            q = q.filter(Item.Category.ilike(category))
        return q.all()

    @staticmethod
    def get_by_name(name):
        return Item.query.filter_by(ItemName=name).first()

    @staticmethod
    def add(name, price, stock, category, reorder_threshold):
        if Item.query.filter_by(ItemName=name).first():
            return None, f'"{name}" already exists'
        item = Item(
            ItemName=name,
            Price=price,
            Stock=stock,
            Category=category or 'Uncategorized',
            reorderThreshold=reorder_threshold
        )
        db.session.add(item)
        db.session.commit()
        return item, None

    @staticmethod
    def update(name, price, stock, category, reorder_threshold):
        item = Item.query.filter_by(ItemName=name).first()
        if not item:
            return None, 'Item not found'
        item.Price            = price
        item.Stock            = stock
        item.Category         = category or item.Category
        item.reorderThreshold = reorder_threshold
        db.session.commit()
        return item, None

    @staticmethod
    def delete(name):
        item = Item.query.filter_by(ItemName=name).first()
        if not item:
            return False, 'Item not found'
        db.session.delete(item)
        db.session.commit()
        return True, None
