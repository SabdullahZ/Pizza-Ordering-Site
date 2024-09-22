import json
from flask import request, jsonify
from flask_restful import Resource, reqparse
from models import Pizza, Cart, Order, Admin, Rider  # Import the Pizza model
from mongoengine import DoesNotExist

# Resource to handle adding a pizza (Admin)
class AdminAuth(Resource):
    def post(self):
        data = json.loads(request.data)  # Use request.data and json.loads to parse the data
        admin = Admin(
            username=data['username'],
            password=data['password']
        )
        # Check if the admin and password is correct
        if admin.username == "admin" and admin.password == "123":
            return jsonify(200)

        return jsonify(403)

class AddPizza(Resource):
    def post(self):
        data = json.loads(request.data)  # Use request.data and json.loads to parse the data
        pizza = Pizza(
            name=data['name'],
            description=data.get('description'),
            price=data['price']
        )
        pizza.save()
        
        # Create the response dictionary directly
        response = {
            "id": str(pizza.id),
            "name": pizza.name,
            "description": pizza.description,
            "price": pizza.price
        }

        return jsonify(response)  # Return the newly created pizza

class RemovePizza(Resource):
    def post(self):
        data = json.loads(request.data)  # Use request.data and json.loads to parse the data
        pizza_id = data['pizza_id']

        pizza = Pizza.objects(id=pizza_id).first()
        if not pizza:
            return jsonify({"message": "Pizza not found!"})

        pizza.delete()

        return jsonify({"message": "Pizza removed successfully!"})

# Resource to get all pizzas (for customers)
class GetPizzas(Resource):
    def get(self):
        pizzas = Pizza.objects()
        
        # Create a response dictionary with a list of pizzas
        response = {
            "pizzas": [{
                "id": str(pizza.id),
                "name": pizza.name,
                "description": pizza.description,
                "price": pizza.price
            } for pizza in pizzas]
        }
        
        return jsonify(response)  # Return the response wrapped in jsonify

class AddToCart(Resource):
    def post(self):
        print("<------ Adding pizza(s) to cart ------->")
        data = request.get_json()
        pizza_ids = data.get('pizza_ids', [])

        # Fetch or create the cart
        cart = Cart.objects.first()  # Adjust this if you have logic to select a specific cart
        if not cart:
            cart = Cart()  # Create a new cart if none exists
            cart.save()

        for pizza_id in pizza_ids:
            pizza = Pizza.objects(id=pizza_id).first()
            if not pizza:
                return jsonify({"message": f"Pizza with ID {pizza_id} not found!"}), 404
            
            # Add pizza to the cart's items
            cart.items.append(pizza)

        # Update the cart's total
        cart.total = sum([pizza.price for pizza in cart.items])

        cart.save()  # Save the updated cart
        return jsonify({"message": "Pizzas added to cart!"})

class GetPizzasInCart(Resource):
    def get(self):
        cart = Cart.objects.first()
        if not cart:
            return jsonify({"message": "Cart not found!"})
        
        # Create a response dictionary with a list of pizzas
        response = {
            "items": [{
                "id": str(pizza.id),
                "name": pizza.name,
                "description": pizza.description,
                "price": pizza.price
            } for pizza in cart.items],
            "total": cart.total
        }

        return jsonify(response)

class RemoveFromCart(Resource):
    def post(self):
        print("<------ Removing pizza from cart ------->")
        data = request.get_json()
        pizza_id = data.get('pizza_id')

        # Fetch the current cart
        cart = Cart.objects.first()  # Adjust if you have a way to fetch the user's cart
        if not cart:
            return jsonify({"message": "Cart not found!"})

        # Find and remove the first matching pizza
        for item in cart.items:
            if str(item.id) == pizza_id:
                cart.items.remove(item)
                # Update the cart's total
                cart.total = sum([pizza.price for pizza in cart.items])
                cart.save()  # Save the updated cart
                return jsonify({"message": "Pizza removed from cart!"})
        
        return jsonify({"message": "Pizza not found in cart!"})

class GetOrders(Resource):
    def get(self):
        orders = Order.objects()
        
        response = {
            "orders": [{
                "total": order.total,
                "id": str(order.id),
                "pizzas": [{
                    "id": str(pizza.id),
                    "name": pizza.name,
                    "price": pizza.price
                } for pizza in order.pizzas],
                "rider_name" : order.assigned_rider
            } for order in orders]
        }
        
        return jsonify(response)


class PlaceOrder(Resource):
    def post(self):
        print("<------ Placing order ------->")
        cart = Cart.objects.first()  # Fetch the cart
        if not cart or not cart.items:
            return jsonify({"message": "Cart is empty or not found!"}), 404
        
        # Create a new order
        order = Order(pizzas=cart.items, total=cart.total)
        order.save()  # Save the order to the database

        # Clear the cart
        cart.items = []  # Clear the list of items
        cart.total = 0.0  # Reset total
        cart.save()  # Save the updated cart

        response = {
            "message": "Order placed successfully!",
            "order_id": str(order.id),  # Optionally return the order ID
            "items": [{
                "id": str(pizza.id),
                "name": pizza.name,
                "description": pizza.description,
                "price": pizza.price
            } for pizza in order.pizzas],
            "total": order.total
        }

        return jsonify(response)

class AddRider(Resource):
    def post(self):
        data = request.get_json()  # Use get_json() for better error handling
        rider_name = data.get('name')  # Get rider's name from the data
        
        if not rider_name:
            return jsonify({"message": "Rider name is required!"}), 400

        # Create a new rider document
        rider = Rider(name=rider_name)
        rider.save()

        # Prepare the response
        response = {
            "message": "Rider added successfully!",
            "id": str(rider.id),
            "name": rider.name
        }

        return jsonify(response)

class GetRiders(Resource):
    def get(self):
        try:
            riders = Rider.objects()  # Fetch all riders
            return {"riders": [{"id": str(rider.id), "name": rider.name} for rider in riders]}, 200
        except Exception as e:
            return {"message": str(e)}, 500



class AssignOrderToRider(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('order_id', type=str, required=True, help='Order ID cannot be blank')
        self.parser.add_argument('rider_name', type=str, required=True, help='Rider name cannot be blank')

    def post(self):
        args = self.parser.parse_args()
        order_id = args['order_id']
        rider_name = args['rider_name']

        try:
            # Find the order by ID
            order = Order.objects.get(id=order_id)
            # Find the rider by name
            rider = Rider.objects.get(name=rider_name)

            # Assign the rider to the order
            order.assigned_rider = rider
            order.save()

            return {
                'message': 'Order assigned to rider successfully',
                'order_id': str(order.id),  # Convert ObjectId to string
                'rider_name': rider.name
            }, 200

        except DoesNotExist:
            return {'message': 'Order or Rider not found'}, 404
        except Exception as e:
            return {'message': str(e)}, 500
