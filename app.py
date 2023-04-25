from flask import Flask,jsonify
from flask_restful import Resource, Api, reqparse, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#To create a Flask app
app = Flask(__name__)

#To make connection with SQLite DataBase
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#To create API
api = Api(app)


db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_name = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'total_price': self.total_price,
            'created_at': self.created_at.isoformat()
        }

#To create a SQLite Database with Users and Orders Table   
with app.app_context():
    db.create_all()


user_parser = reqparse.RequestParser()
user_parser.add_argument('name', type=str, required=True)
user_parser.add_argument('email', type=str, required=True)

order_parser = reqparse.RequestParser()
order_parser.add_argument('user_id', type=int, required=True)
order_parser.add_argument('product_name', type=str, required=True)
order_parser.add_argument('quantity', type=int, required=True)
order_parser.add_argument('total_price', type=float, required=True)

class UserDetails(Resource):
    def get(self, user_id=None):
        if user_id is None:
            users = User.query.all()
            return jsonify([user.to_dict() for user in users])
        else:
            user = User.query.get_or_404(user_id)
            return jsonify(user.to_dict())

    def post(self):
        args = user_parser.parse_args()
        name = args['name']
        email = args['email']
        user = User(name=name, email=email)
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User created successfully!'})

class OrderDetails(Resource):
    def get(self, order_id=None):
        if order_id is None:
            orders = Order.query.all()
            return jsonify([order.to_dict() for order in orders])
        else:
            order = Order.query.get_or_404(order_id)
            return jsonify(order.to_dict())

    def post(self):
        args = order_parser.parse_args()
        user_id = args['user_id']
        product_name = args['product_name']
        quantity = args['quantity']
        total_price = args['total_price']
        order = Order(user_id=user_id, product_name=product_name, quantity=quantity, total_price=total_price)
        db.session.add(order)
        db.session.commit()
        return jsonify({'message': 'Order created successfully!'})

api.add_resource(UserDetails, '/users', '/users/<int:user_id>')
api.add_resource(OrderDetails, '/orders', '/orders/<int:order_id>')


if __name__ == '__main__':
    app.run(debug=True)
