from flask import render_template, request, redirect, url_for, flash, session, abort
from app import app, db
from models import Customer, Admin
from forms import CustomerForm, AdminLoginForm, DeleteConfirmForm
from sqlalchemy import or_

# Helper function to check admin authentication
def is_admin_logged_in():
    return 'admin_id' in session

# Customer management routes (public access)
@app.route('/')
def customer_list():
    search = request.args.get('search', '').strip()
    
    if search:
        customers = Customer.query.filter(
            or_(
                Customer.name.ilike(f'%{search}%'),
                Customer.email.ilike(f'%{search}%'),
                Customer.phone.ilike(f'%{search}%')
            )
        ).order_by(Customer.created_at.desc()).all()
    else:
        customers = Customer.query.order_by(Customer.created_at.desc()).all()
    
    return render_template('customer_list.html', customers=customers, search=search)

@app.route('/customer/create', methods=['GET', 'POST'])
def customer_create():
    form = CustomerForm()
    
    if form.validate_on_submit():
        customer = Customer(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data or None
        )
        
        try:
            db.session.add(customer)
            db.session.commit()
            flash('Customer created successfully!', 'success')
            return redirect(url_for('customer_list'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating customer. Please try again.', 'error')
            app.logger.error(f"Error creating customer: {e}")
    
    return render_template('customer_form.html', form=form, title='Add New Customer')

@app.route('/customer/edit/<int:customer_id>', methods=['GET', 'POST'])
def customer_edit(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    form = CustomerForm(customer_id=customer_id, obj=customer)
    
    if form.validate_on_submit():
        customer.name = form.name.data
        customer.email = form.email.data
        customer.phone = form.phone.data or None
        
        try:
            db.session.commit()
            flash('Customer updated successfully!', 'success')
            return redirect(url_for('customer_list'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating customer. Please try again.', 'error')
            app.logger.error(f"Error updating customer: {e}")
    
    return render_template('customer_form.html', form=form, customer=customer, title='Edit Customer')

@app.route('/customer/delete/<int:customer_id>', methods=['GET', 'POST'])
def customer_delete(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    form = DeleteConfirmForm()
    
    if form.validate_on_submit():
        try:
            db.session.delete(customer)
            db.session.commit()
            flash('Customer deleted successfully!', 'success')
            return redirect(url_for('customer_list'))
        except Exception as e:
            db.session.rollback()
            flash('Error deleting customer. Please try again.', 'error')
            app.logger.error(f"Error deleting customer: {e}")
    
    return render_template('customer_delete.html', customer=customer, form=form)

# Admin authentication routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin_logged_in():
        return redirect(url_for('admin_dashboard'))
    
    form = AdminLoginForm()
    
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        
        if admin and admin.check_password(form.password.data):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin_login.html', form=form)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('customer_list'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin_logged_in():
        flash('Please log in to access the admin dashboard', 'error')
        return redirect(url_for('admin_login'))
    
    total_customers = Customer.query.count()
    recent_customers = Customer.query.order_by(Customer.created_at.desc()).limit(5).all()
    
    return render_template('admin_dashboard.html', 
                         total_customers=total_customers, 
                         recent_customers=recent_customers)

@app.route('/admin/customers')
def admin_customer_list():
    if not is_admin_logged_in():
        flash('Please log in to access admin features', 'error')
        return redirect(url_for('admin_login'))
    
    search = request.args.get('search', '').strip()
    
    if search:
        customers = Customer.query.filter(
            or_(
                Customer.name.ilike(f'%{search}%'),
                Customer.email.ilike(f'%{search}%'),
                Customer.phone.ilike(f'%{search}%')
            )
        ).order_by(Customer.created_at.desc()).all()
    else:
        customers = Customer.query.order_by(Customer.created_at.desc()).all()
    
    return render_template('customer_list.html', customers=customers, search=search, admin_view=True)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('base.html', content='<h2>Page Not Found</h2><p>The page you are looking for does not exist.</p>'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('base.html', content='<h2>Internal Server Error</h2><p>Something went wrong. Please try again later.</p>'), 500
