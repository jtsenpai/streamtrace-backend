from decimal import Decimal

def monthly_equivalent(price: Decimal, cycle: str, custom_days: int = 0) -> Decimal:
    if not price:
        return Decimal("0")
    cycle = (cycle or "").lower()
    if cycle == "monthly":
        return Decimal(price)
    if cycle == "yearly":
        return Decimal(price) / Decimal("12")
    # custom days -> approx months
    days = custom_days or 30
    return (Decimal(price) * Decimal(days)) / Decimal("30")

def yearly_equivalent(price: Decimal, cycle: str, custom_days: int = 0) -> Decimal:
    if not price:
        return Decimal("0")
    cycle = (cycle or "").lower()
    if cycle == "monthly":
        return Decimal(price) * Decimal("12")
    if cycle == "yearly":
        return Decimal(price)
    days = custom_days or 30
    # 12 “30-day months”
    return (Decimal(price) * Decimal(days) * Decimal("12")) / Decimal("30")
