from enum import StrEnum


class OrderStatus(StrEnum):
    NEW = "new"
    PARTIALLY_FILLED = "partially_filled"
    FULLY_FILLED = "fully_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class Order:
    def __init__(self, symbol, side, quantity):
        self.symbol = symbol
        self.side = side
        self.quantity = quantity
        self.filled_quantity = 0
        self.status = OrderStatus.NEW
        self.fills = []

    def apply_fill(self, fill_quantity, fill_price):
        if self.status not in (OrderStatus.NEW, OrderStatus.PARTIALLY_FILLED):
            raise ValueError(f"Cannot apply fill to {self.status} order")
        new_total_filled = self.filled_quantity + fill_quantity
        if new_total_filled > self.quantity:
            raise ValueError("Fill exceeds remaining quantity")
        if fill_quantity <= 0:
            raise ValueError("Fill quantity cannot be 0 or negative")
        if fill_price <= 0:
            raise ValueError("Fill price cannot be 0 or negative")
        self.filled_quantity = new_total_filled
        if new_total_filled == self.quantity:
            self.status = OrderStatus.FULLY_FILLED
        elif new_total_filled < self.quantity:
            self.status = OrderStatus.PARTIALLY_FILLED
        self.fills.append({"quantity": fill_quantity, "price": fill_price})

    def calculate_volume_weighted_average_price(self):
        if not self.fills:
            return None
        total_quantity = sum(fill["quantity"] for fill in self.fills)
        total_cost = sum(fill["quantity"] * fill["price"] for fill in self.fills)
        return total_cost / total_quantity

    def cancel(self):
        if self.status not in (OrderStatus.NEW, OrderStatus.PARTIALLY_FILLED):
            raise ValueError(f"Cannot cancel {self.status} order")
        self.status = OrderStatus.CANCELLED

    def reject(self):
        if self.status != OrderStatus.NEW:
            raise ValueError(f"Cannot reject {self.status} order")
        self.status = OrderStatus.REJECTED
