from flask import Blueprint
from flask_restful import Api
from resources import AdminAuth, AddPizza, RemovePizza, GetPizzas, AddToCart, GetPizzasInCart, RemoveFromCart, GetOrders, PlaceOrder

# Create a Blueprint for the API
api_bp = Blueprint('api', __name__)

# Initialize the API with the Blueprint
api = Api(api_bp)

# Register resources using add_resource
api.add_resource(AdminAuth, '/api/login')       # POST - Login
api.add_resource(AddPizza, '/api/addPizza')        # POST - Add pizza
api.add_resource(RemovePizza, '/api/removePizza')  # POST - Remove pizza
api.add_resource(GetPizzas, '/api/pizzas')      # GET - Get all pizzas
api.add_resource(AddToCart, '/api/addToCart')   # POST - Add pizza to cart
api.add_resource(GetPizzasInCart, '/api/cart')   # GET - Get pizzas in cart
api.add_resource(RemoveFromCart, '/api/removeFromCart')  # POST - Remove pizza from cart
api.add_resource(GetOrders, '/api/orders')     # GET - Get orders
api.add_resource(PlaceOrder, '/api/placeOrder')  # POST - Place order