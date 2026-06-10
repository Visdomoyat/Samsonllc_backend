from decimal import Decimal, ROUND_HALF_UP

def stack_blend_line_total(unit_price: Decimal, quantity: int) -> Decimal:
    """Bundle pricing: 1=standard, 2=5% off, 3=10% off, 4+=3@10% + rest@standard."""
    if quantity <= 0:
        return Decimal('0.00')

    price = Decimal(unit_price)
    if quantity == 1:
        total = price
    elif quantity == 2:
        total = price * 2 * Decimal('0.95')
    elif quantity == 3:
        total = price * 3 * Decimal('0.90')
    else:
        total = price * 3 * Decimal('0.90') + price * (quantity - 3)

    return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def stack_blend_effective_unit_price(unit_price: Decimal, quantity: int) -> Decimal:
    if quantity <= 0:
        return Decimal('0.00')
    return (stack_blend_line_total(unit_price, quantity) / quantity).quantize(
        Decimal('0.01'),
        rounding=ROUND_HALF_UP,
    )


def stack_blend_bundle_tiers(unit_price: Decimal) -> list[dict]:
    """Pricing tiers for storefront display."""
    price = Decimal(unit_price)
    tiers = [
        {
            'quantity': 1,
            'discount_percent': 0,
            'line_total': str(stack_blend_line_total(price, 1)),
            'label': 'Standard price',
        },
        {
            'quantity': 2,
            'discount_percent': 5,
            'line_total': str(stack_blend_line_total(price, 2)),
            'label': '5% off',
        },
        {
            'quantity': 3,
            'discount_percent': 10,
            'line_total': str(stack_blend_line_total(price, 3)),
            'label': '10% off',
        },
        {
            'quantity': 4,
            'discount_percent': None,
            'line_total': str(stack_blend_line_total(price, 4)),
            'label': '3 at 10% off + additional at standard price',
        },
    ]
    return tiers
