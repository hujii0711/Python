from dataclasses import dataclass, field


@dataclass
class Product:
    name: str
    price: float
    quantity: int = 1

    def total(self) -> float:
        return self.price * self.quantity


@dataclass
class Cart:
    owner: str
    items: list[Product] = field(default_factory=list)

    def add(self, product: Product):
        self.items.append(product)

    def grand_total(self) -> float:
        return sum(item.total() for item in self.items)


cart = Cart(owner="Bob")
cart.add(Product("사과", 1500, 3))
cart.add(Product("우유", 2800))

print(cart)
# Cart(owner='Bob', items=[Product(name='사과', price=1500, quantity=3), ...])

print(f"총 금액: {cart.grand_total():,}원")  # 총 금액: 7,300원
