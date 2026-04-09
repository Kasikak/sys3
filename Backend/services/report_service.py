from models import db, Sale, Item, Report
from datetime import datetime, timezone


class ReportService:

    @staticmethod
    def generate(start_str, end_str, user_id):
        """
        Build a report for the given date range.
        Returns (data_dict, error)
        """
        try:
            date_from = datetime.strptime(start_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            date_to   = datetime.strptime(end_str,   '%Y-%m-%d').replace(
                            hour=23, minute=59, second=59, tzinfo=timezone.utc)
        except ValueError:
            return None, 'Invalid date format'

        sales = Sale.query.filter(Sale.date >= date_from, Sale.date <= date_to).all()

        total_revenue    = round(sum(s.total for s in sales), 2)
        total_items_sold = sum(si.quantity for s in sales for si in s.saleItems)

        # Per-product totals
        product_map = {}
        for s in sales:
            for si in s.saleItems:
                if si.ItemName not in product_map:
                    product_map[si.ItemName] = {'name': si.ItemName, 'qty': 0, 'revenue': 0.0}
                product_map[si.ItemName]['qty']     += si.quantity
                product_map[si.ItemName]['revenue'] += round(si.quantity * si.priceAtSale, 2)

        top_products = sorted(product_map.values(), key=lambda x: x['revenue'], reverse=True)[:10]

        # Daily breakdown
        daily_map = {}
        for s in sales:
            day = s.date.strftime('%Y-%m-%d')
            if day not in daily_map:
                daily_map[day] = {'date': day, 'total': 0.0, 'count': 0}
            daily_map[day]['total'] = round(daily_map[day]['total'] + s.total, 2)
            daily_map[day]['count'] += 1
        sales_by_day = sorted(daily_map.values(), key=lambda x: x['date'])

        # Stock counts
        items = Item.query.all()
        low_stock_count    = sum(1 for i in items if 0 < i.Stock <= i.reorderThreshold)
        out_of_stock_count = sum(1 for i in items if i.Stock == 0)

        # Log the report
        db.session.add(Report(
            generatedBy=user_id,
            reportType='OnDemand',
            dateRangeFrom=date_from,
            dateRangeTo=date_to
        ))
        db.session.commit()

        return {
            'total_revenue':      total_revenue,
            'total_sales':        len(sales),
            'total_items_sold':   total_items_sold,
            'low_stock_count':    low_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'top_products':       top_products,
            'sales_by_day':       sales_by_day
        }, None
