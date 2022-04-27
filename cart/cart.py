from decimal import Decimal
from cart.forms import CartAddProductForm
from products.models import Product
import copy

class Cart:
    def __init__(self, request):
        if request.session.get('cart') is None:
            request.session['cart'] = {}

        self.cart = request.session['cart']
        self.session = request.session

    def __iter__(self):
        cart = copy.deepcopy(self.cart)

        for product_id in cart:
            prod_id = str(product_id)
            product = cart[prod_id]
            product['price'] = Decimal(product['price'])
            product['total_price'] = product['price'] * product['quantity']
            product['product'] = Product.objects.get(id=prod_id)
            product['update_quantity_form'] = CartAddProductForm(
                initial={'quantity': product['quantity'], 'override':True}
            )

            yield product

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def add(self, product, quantity=1, override_quantity=False):
        total_quantity = quantity
        product_id = str(product.id)

        if product_id in self.cart:
            total_quantity += self.cart[product_id]['quantity']

        if override_quantity:
            total_quantity = quantity
        
        if total_quantity > 20:
                total_quantity = 20

        self.cart[product_id] = {'quantity': total_quantity, 'price': str(product.price)}

        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
 
    def save(self):
        self.session.modified = True

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())