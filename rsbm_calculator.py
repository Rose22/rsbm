def total_price(items, only_paid=False):
    total_price = 0.00
    for item in items:
        if only_paid and not item['paid']:
            continue

        total_price += float(item['price'])

    return total_price

def total_price_bills(monthly_bills, only_paid=False):
    total_price_bills = 0.00
    for bill in monthly_bills:
        if only_paid and not bill['paid']:
            continue

        total_price_bills += float(bill['price'])

    return total_price_bills

def total_budgetable(income, monthly_bills):
    return float(income)-total_price_bills(monthly_bills)
