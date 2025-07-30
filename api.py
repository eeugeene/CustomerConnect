
import functools
from flask import Blueprint, jsonify, request, session
from .models import Customer, Admin
from .app import db
from datetime import datetime, timedelta
from sqlalchemy import func

# Create a Blueprint for the API
api_bp = Blueprint('api', __name__, url_prefix='/api')

# --- API Authentication (Simple Token-Based) ---
# In a real app, use something more robust like Flask-JWT-Extended or OAuth2

def token_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # For simplicity, we'll check if the admin is logged in via session.
        # A true mobile app API would use a header token (e.g., 'X-API-KEY').
        if 'admin_id' not in session:
            return jsonify({"message": "Authentication is required"}), 401
        return f(*args, **kwargs)
    return decorated_function

# --- Customer API Endpoints ---

@api_bp.route('/customers', methods=['GET'])
@token_required
def get_customers():
    """Return a list of all customers."""
    customers = Customer.query.order_by(Customer.created_at.desc()).all()
    return jsonify([c.to_dict() for c in customers])

@api_bp.route('/customers', methods=['POST'])
@token_required
def create_customer():
    """Create a new customer."""
    data = request.get_json()
    if not data or not 'name' in data or not 'email' in data:
        return jsonify({"message": "Missing name or email"}), 400

    customer = Customer(
        name=data['name'],
        email=data['email'],
        phone=data.get('phone')
    )
    db.session.add(customer)
    db.session.commit()
    return jsonify(customer.to_dict()), 201

@api_bp.route('/customers/<int:customer_id>', methods=['GET'])
@token_required
def get_customer(customer_id):
    """Return a single customer."""
    customer = Customer.query.get_or_404(customer_id)
    return jsonify(customer.to_dict())

@api_bp.route('/customers/<int:customer_id>', methods=['PUT'])
@token_required
def update_customer(customer_id):
    """Update an existing customer."""
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json()
    
    customer.name = data.get('name', customer.name)
    customer.email = data.get('email', customer.email)
    customer.phone = data.get('phone', customer.phone)
    
    db.session.commit()
    return jsonify(customer.to_dict())

@api_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
@token_required
def delete_customer(customer_id):
    """Delete a customer."""
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer deleted successfully"}), 200

# --- Analytics API Endpoints ---

@api_bp.route('/analytics/summary', methods=['GET'])
@token_required
def get_analytics_summary():
    """Return key analytics metrics."""
    total_customers = db.session.query(func.count(Customer.id)).scalar()
    
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    new_this_week = db.session.query(func.count(Customer.id)).filter(Customer.created_at >= seven_days_ago).scalar()

    return jsonify({
        "total_customers": total_customers,
        "new_this_week": new_this_week
    })

@api_bp.route('/analytics/timeseries', methods=['GET'])
@token_required
def get_analytics_timeseries():
    """Return customer creation counts for the last 30 days."""
    thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)
    
    results = db.session.query(
        func.date(Customer.created_at).label('date'),
        func.count(Customer.id).label('count')
    ).filter(func.date(Customer.created_at) >= thirty_days_ago).group_by('date').order_by('date').all()

    # Convert results to a list of dictionaries
    timeseries = [{"date": r.date.isoformat(), "count": r.count} for r in results]
    
    return jsonify(timeseries)

# --- API Login Endpoint ---
# This allows the mobile app to authenticate.

@api_bp.route('/login', methods=['POST'])
def api_login():
    """Authenticate and create a session for the API."""
    data = request.get_json()
    if not data or not 'username' in data or not 'password' in data:
        return jsonify({"message": "Missing username or password"}), 400

    admin = Admin.query.filter_by(username=data['username']).first()

    if admin and admin.check_password(data['password']):
        session.clear()
        session['admin_id'] = admin.id
        session['admin_username'] = admin.username
        return jsonify({"message": "Login successful"}), 200
    
    return jsonify({"message": "Invalid credentials"}), 401
