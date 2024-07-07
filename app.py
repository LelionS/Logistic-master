from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo
import json
import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64
import os
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, SelectField, HiddenField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'avif', 'webp'}

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Load availability from JSON file
def load_availability():
    if os.path.exists('availability.json'):
        with open('availability.json', 'r') as file:
            return json.load(file)
    return {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
# Save availability to JSON file
def save_availability(viewer, availability, updater):
    data = load_availability()
    data[viewer] = {'availability': availability, 'updater': updater}
    with open('availability.json', 'w') as file:
        json.dump(data, file)

# Load users from JSON file
def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as file:
            return json.load(file)
    return {}

# Save users to JSON file
def save_users(users):
    with open('users.json', 'w') as file:
        json.dump(users, file)

# Load items from JSON file
def load_items():
    with open('items.json') as f:
        return json.load(f)

def load_items():
    if os.path.exists('items.json'):
        with open('items.json', 'r') as file:
            return json.load(file)
    return {}

# Save items to JSON file
def save_items(items):
    with open('items.json', 'w') as file:
        json.dump(items, file)

# Load carts from JSON file
def load_carts():
    if os.path.exists('carts.json'):
        with open('carts.json', 'r') as file:
            return json.load(file)
    return {}

# Save carts to JSON file
def save_carts(carts):
    with open('carts.json', 'w') as file:
        json.dump(carts, file)

# Load orders from JSON file
# Example of how load_orders() might look:
def load_orders():
    try:
        with open('orders.json', 'r') as file:
            orders = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        orders = {}
    return orders


# Save orders to JSON file
def save_orders(orders):
    with open('orders.json', 'w') as file:
        json.dump(orders, file)

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, username, password, role, approved=True):
        self.id = username
        self.password = password
        self.role = role
        self.approved = approved

# Flask-WTF forms
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('updater', 'driver'), ('viewer', 'customer')], validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UpdateForm(FlaskForm):
    viewer = SelectField('customer', choices=[], validators=[DataRequired()])
    availability = StringField('Availability', validators=[DataRequired()])
    submit = SubmitField('Update')

class ItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    quantity = StringField('Quantity', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])
    submit = SubmitField('Save Item')

class CartForm(FlaskForm):
    item = SelectField('Item', choices=[], validators=[DataRequired()])
    quantity = StringField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Add to Cart')

class OrderForm(FlaskForm):
    submit = SubmitField('Checkout')

class AssignOrderForm(FlaskForm):
    updater = SelectField('driver', choices=[], validators=[DataRequired()])

class UpdateOrderStatusForm(FlaskForm):
    viewer_username = StringField('customer Username', validators=[DataRequired()])
    updater = StringField('Driver')  # Add this line
    submit = SubmitField('Submit')

# Dummy data for demonstration
items = {
    '1': {'name': 'Item 1', 'quantity': 10, 'price': 20.0},
    '2': {'name': 'Item 2', 'quantity': 5, 'price': 15.0},
    '3': {'name': 'Item 3', 'quantity': 8, 'price': 30.0}
}

# Flask-WTF form for editing an item
class EditItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=50)])
    quantity = StringField('Quantity', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])
    submit = SubmitField('Update')

class MpesaC2bCredential:
    consumer_key = 'D6UVFW0NqI4Sir9HdLMeJIlGy0yX6YVXi76348J2yfnnlkev' 
    consumer_secret = 'qmhTOxyzaJfxYtlt0y2bZm7uORobP46TNG8t24KpNCxOAL6TnGdh65DAQPZYD4IL' 
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

class MpesaAccessToken:
    r = requests.get(MpesaC2bCredential.api_URL,
                     auth=HTTPBasicAuth(MpesaC2bCredential.consumer_key, MpesaC2bCredential.consumer_secret))
    mpesa_access_token = r.json()
    formated_res = json.dumps(mpesa_access_token, indent=4)
    validated_mpesa_access_token = mpesa_access_token['access_token']
    print(formated_res)

class LipanaMpesaPpassword:
    lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
    Business_short_code = "174379"
    passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
    data_to_encode = Business_short_code + passkey + lipa_time
    online_password = base64.b64encode(data_to_encode.encode())
    decode_password = online_password.decode('utf-8')

@login_manager.user_loader
def load_user(user_id):
    users = load_users()
    if user_id in users:
        user = users[user_id]
        role = user.get('role', 'viewer')  # Default to 'viewer' if 'role' is missing
        approved = user.get('approved', True)  # Default to True if 'approved' is missing
        return User(username=user_id, password=user['password'], role=role, approved=approved)
    return None

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/display_availability')
def home():
    return redirect(url_for('display_availability'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        users = load_users()
        if form.username.data in users:
            flash('Username already exists. Please choose a different one.')
        else:
            approved = form.role.data == 'viewer'  # Viewers are automatically approved
            users[form.username.data] = {'password': form.password.data, 'role': form.role.data, 'approved': approved}
            save_users(users)
            if approved:
                flash('Registration successful. You can now log in.')
            else:
                flash('Registration successful. Awaiting admin approval.')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        users = load_users()
        if form.username.data in users:
            user = users[form.username.data]
            if user['password'] == form.password.data:
                if user['role'] == 'updater' and not user.get('approved', True):
                    flash('Your account is awaiting admin approval.')
                else:
                    login_user(User(username=form.username.data, password=form.password.data, role=user['role'], approved=user.get('approved', True)))
                    flash('Login successful.')
                    return redirect(url_for('home'))
            else:
                flash('Invalid username or password.')
        else:
            flash('Invalid username or password.')
    return render_template('login.html', form=form)

@app.route('/terms_and_conditions')
def terms_and_conditions():
    return render_template('terms_and_conditions.html')

@app.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/updater_dashboard', methods=['GET', 'POST'])
@login_required
def updater_dashboard():
    if current_user.role != 'updater':
        flash('You do not have permission to access this page.')
        return redirect(url_for('display_availability'))

    form = UpdateForm()

    users = load_users()
    viewers = [(username, username) for username, details in users.items() if details['role'] == 'viewer']
    form.viewer.choices = viewers

    if form.validate_on_submit():
        availability = form.availability.data
        viewer = form.viewer.data
        save_availability(viewer, availability, current_user.id)
        flash('Availability updated successfully.')
        return redirect(url_for('display_availability'))

    return render_template('updater_dashboard.html', form=form)


# Route for managing pending deliveries (example)
@app.route('/updater/pending_deliveries', methods=['GET', 'POST'])
@login_required
def pending_deliveries():
    if current_user.role != 'updater':
        flash('You do not have permission to access this page.')
        return redirect(url_for('home'))

    if request.method == 'POST':
        delivery_id = request.form.get('delivery_id')
        # Update the order status to 'Assigned' and assign the updater
        orders = load_orders()
        if delivery_id in orders and orders[delivery_id]['status'] == 'Pending':
            orders[delivery_id]['status'] = 'Assigned'
            orders[delivery_id]['updater'] = current_user.id
            save_orders(orders)
            flash(f'Delivery {delivery_id} assigned to you.')
            return redirect(url_for('my_deliveries'))

    pending_orders = load_orders().values()  # Load all orders
    return render_template('pending_deliveries.html', pending_orders=pending_orders)

@app.route('/updater/my_deliveries')
@login_required
def my_deliveries():
    if current_user.role != 'updater':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))

    orders = load_orders()
    my_deliveries = {user: order for user, order in orders.items() if order.get('updater') == current_user.id}
    return render_template('my_deliveries.html', my_deliveries=my_deliveries)

@app.route('/updater/update_status/<username>', methods=['POST'])
@login_required
def update_status(username):
    if current_user.role != 'updater':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('home'))

    orders = load_orders()
    if username in orders:
        order = orders[username]
        if order['status'] == 'Delivered':
            flash('Cannot update status. Delivery is already marked as Delivered.', 'warning')
        else:
            status = request.form.get('status')
            if status in ['Pending', 'Delivered', 'Cancelled']:
                order['status'] = status
                save_orders(orders)
                flash(f'Status updated to {status} for delivery of {username}.', 'success')
            else:
                flash('Invalid status update.', 'danger')
    else:
        flash('Order not found.', 'danger')

    return redirect(url_for('my_deliveries'))

@app.route('/display')
@login_required
def display_availability():
    data = load_availability()
    user_data = data.get(current_user.id, {})
    availability = user_data.get('availability', 'No availability set')
    updater = user_data.get('updater', 'Unknown')
    return render_template('display.html', availability=availability, updater=updater)

@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.')
        return redirect(url_for('home'))

    users = load_users()

    viewers = {username: details for username, details in users.items() if details['role'] == 'viewer'}
    updaters_pending = {username: details for username, details in users.items() if details['role'] == 'updater' and not details.get('approved', True)}
    updaters_approved = {username: details for username, details in users.items() if details['role'] == 'updater' and details.get('approved', True)}

    return render_template('admin.html', viewers=viewers, updaters_pending=updaters_pending, updaters_approved=updaters_approved)

@app.route('/approve/<username>')
@login_required
def approve_user(username):
    if current_user.role != 'admin':
        flash('You do not have permission to perform this action.')
        return redirect(url_for('home'))

    users = load_users()
    if username in users and users[username]['role'] == 'updater':
        users[username]['approved'] = True
        save_users(users)
        flash(f'User {username} has been approved.')
    return redirect(url_for('admin'))

@app.route('/reject/<username>')
@login_required
def reject_user(username):
    if current_user.role != 'admin':
        flash('You do not have permission to perform this action.')
        return redirect(url_for('home'))

    users = load_users()
    if username in users and users[username]['role'] == 'updater':
        del users[username]
        save_users(users)
        flash(f'User {username} has been rejected.')
    return redirect(url_for('admin'))

@app.route('/admin/manage_items/add', methods=['GET', 'POST'])
@login_required
def add_item():
    form = ItemForm()
    if form.validate_on_submit():
        items = load_items()
        new_id = str(len(items) + 1)  # Generate a new ID
        new_item = {
            'name': form.name.data,
            'quantity': form.quantity.data,
            'price': form.price.data,
            'image': 'default.png'  # You can adjust this default value as needed
        }
        items[new_id] = new_item
        save_items(items)
        flash('Item added successfully.', 'success')
        return redirect(url_for('admin_items'))

    return render_template('add_item.html', form=form)
@app.route('/admin/manage_items/edit/<item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    form = ItemForm()
    items = load_items()
    item = items.get(item_id)

    if not item:
        flash('Item not found.', 'danger')
        return redirect(url_for('admin_items'))

    if form.validate_on_submit():
        item['name'] = form.name.data
        item['quantity'] = form.quantity.data
        item['price'] = form.price.data
        save_items(items)
        flash('Item updated successfully.', 'success')
        return redirect(url_for('admin_items'))

    form.name.data = item['name']
    form.quantity.data = item['quantity']
    form.price.data = item['price']

    return render_template('edit_item.html', form=form, item_id=item_id)

@app.route('/admin/manage_items/delete/<item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    items = load_items()
    if item_id in items:
        del items[item_id]
        save_items(items)
        flash('Item deleted successfully.', 'success')
    else:
        flash('Item not found.', 'danger')

    return redirect(url_for('admin_items'))


@app.route('/admin/order/<username>/delete', methods=['POST'])
@login_required
def delete_order(username):
    if current_user.role != 'admin':
        flash('You do not have permission to perform this action.')
        return redirect(url_for('home'))

    orders = load_orders()
    if username in orders:
        del orders[username]
        save_orders(orders)
        flash(f'Order for {username} has been deleted.', 'success')
    else:
        flash(f'Order for {username} not found.', 'danger')
    
    return redirect(url_for('admin_orders'))

@app.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    form = CartForm()
    items = load_items()
    form.item.choices = [(item_id, details['name']) for item_id, details in items.items()]

    carts = load_carts()
    user_cart = carts.get(current_user.id, {})

    cart_items = []
    for item_id, quantity in user_cart.items():
        if item_id in items:
            item_details = items[item_id]
            cart_items.append({
                'id': item_id,
                'name': item_details['name'],
                'quantity': quantity,
                'price': item_details['price']
            })

    if form.validate_on_submit():
        item_id = form.item.data
        quantity = int(form.quantity.data)
        if item_id in user_cart:
            user_cart[item_id] += quantity
        else:
            user_cart[item_id] = quantity
        carts[current_user.id] = user_cart
        save_carts(carts)
        flash('Item added to cart.')
        return redirect(url_for('cart'))

    return render_template('cart.html', form=form, cart_items=cart_items)


@app.route('/make_order', methods=['GET', 'POST'])
def make_order():
    if request.method == 'POST':
        # Check if 'destination' is in the form data
        if 'destination' in request.form:
            destination = request.form['destination']
            return redirect(url_for('make_payment', destination=destination))
        else:
            # Handle case where 'destination' is not in the form data
            # Redirect or render an error page
            return redirect(url_for('map_page'))  # Redirect to map page or handle differently
    destination = request.args.get('destination', '')
    return render_template('make_order.html', destination=destination)
@app.route('/map', methods=['GET', 'POST'])  # Support both GET and POST methods
def map_page():
    if request.method == 'POST':
        # Handle the form submission from the map page if needed
        # Example: process the selected destination
        selected_destination = request.form.get('selected_destination')
        # Logic to handle the selected destination
        
        # Redirect to the make_order page or handle as needed
        return redirect(url_for('make_order', destination=selected_destination))
    
    # Render the map page template for GET requests
    return render_template('map.html')

@app.route('/get_coordinates', methods=['POST'])
def get_coordinates():
    data = request.json
    lat = data['lat']
    lon = data['lon']
    return jsonify(latitude=lat, longitude=lon)

@app.route('/make_payment', methods=['GET', 'POST'])
def make_payment():
    destination = request.args.get('destination', '')
    if request.method == 'POST':
        name = request.form['name']
        phone = int(request.form['phone'])
        country_code = '254'
        full_phone = country_code + str(phone)
        amount = request.form['amount']
        
        data = {
            "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
            "Password": LipanaMpesaPpassword.decode_password,
            "Timestamp": LipanaMpesaPpassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": int(full_phone),
            "PartyB": LipanaMpesaPpassword.Business_short_code,
            "PhoneNumber": int(full_phone),
            "CallBackURL": "https://your.callback.url/Callback_main/callbackurl_prjct.php",
            "AccountReference": "Lelion",
            "TransactionDesc": "Testing stk push"
        }
        response = lipa_na_mpesa_online(data)
        return render_template('payment.html', destination=destination, message=response)
    
    return render_template('payment.html', destination=destination)

def lipa_na_mpesa_online(data):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": "Bearer %s" % access_token}

    res = requests.post(api_url, json=data, headers=headers).json()
    print(json.dumps(res, indent=4))
    try:
        return res["ResponseDescription"]
    except:
        return res["errorMessage"]

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    carts = load_carts()
    user_cart = carts.pop(current_user.id, {})
    save_carts(carts)

    orders = load_orders()
    orders[current_user.id] = {'cart': user_cart, 'status': 'Pending'}
    save_orders(orders)

    flash('Order placed successfully.')
    return redirect(url_for('map_page'))


@app.route('/updater/orders', methods=['GET', 'POST'])
@login_required
def updater_orders():
    if current_user.role != 'updater':
        flash('You do not have permission to access this page.')
        return redirect(url_for('home'))

    form = UpdateOrderStatusForm()  # Form to update order status
    if form.validate_on_submit():
        order_id = form.order_id.data
        new_status = form.status.data
        orders = load_orders()

        if order_id in orders:
            order = orders[order_id]
            if order['status'] == 'Assigned' and order['updater'] == current_user.username:
                order['status'] = new_status
                save_orders(orders)
                flash(f'Order ID {order_id} status updated to {new_status}.')
            else:
                flash('You can only update orders that are assigned to you and are currently assigned.')
        else:
            flash(f'Order ID {order_id} not found.')

        return redirect(url_for('updater_orders'))

    orders = load_orders()
    assigned_orders = {order_id: order for order_id, order in orders.items() if order['status'] == 'Assigned' and order['updater'] == current_user.username}

    return render_template('updater_orders.html', form=form, orders=assigned_orders)

@app.route('/viewer/orders', methods=['GET', 'POST'])
def viewer_orders():
    form = UpdateOrderStatusForm()

    if form.validate_on_submit():
        viewer_username = form.viewer_username.data
        updater = form.updater.data
        # Example logic to fetch orders based on viewer_username
        orders = [] 
        return render_template('viewer_orders.html', form=form, orders=orders)

    # If GET request or form not submitted yet, render the form
    return render_template('viewer_orders.html', form=form)


@app.route('/admin/order/<username>/accept')
@login_required
def accept_order(username):
    if current_user.role != 'admin':
        flash('You do not have permission to perform this action.')
        return redirect(url_for('home'))

    orders = load_orders()
    if username in orders:
        orders[username]['status'] = 'Accepted'
        save_orders(orders)
        flash('Order accepted.')
    return redirect(url_for('admin_orders'))

@app.route('/admin/order/<username>/decline')
@login_required
def decline_order(username):
    if current_user.role != 'admin':
        flash('You do not have permission to perform this action.')
        return redirect(url_for('home'))

    orders = load_orders()
    if username in orders:
        orders[username]['status'] = 'Declined'
        save_orders(orders)
        flash('Order declined.')
    return redirect(url_for('admin_orders'))

@app.route('/admin/orders', methods=['GET', 'POST'])
@login_required
def admin_orders():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.')
        return redirect(url_for('home'))

    form = AssignOrderForm()
    orders = load_orders()
    users = load_users()

    # Prepare a list of updaters
    updaters = [(username, username) for username, details in users.items() if details['role'] == 'updater' and details.get('approved', True)]
    form.updater.choices = updaters

    if form.validate_on_submit():
        # Assign each pending order to an updater individually
        for user, order in orders.items():
            if order['status'] == 'Pending':
                updater = form.updater.data  
                orders[user]['updater'] = updater
                orders[user]['status'] = 'Assigned'
        save_orders(orders)
        flash('Orders have been assigned.')
        return redirect(url_for('admin_orders'))

    # Filter orders
    pending_orders = {user: order for user, order in orders.items() if order['status'] == 'Pending'}
    delivered_orders = {user: order for user, order in orders.items() if order['status'] == 'Delivered'}

    return render_template('admin_orders.html', form=form, pending_orders=pending_orders, delivered_orders=delivered_orders)


@app.route('/my_orders')
@login_required
def my_orders():
    if current_user.role == 'viewer':
        orders = load_orders()
        viewer_orders = {order_id: order for order_id, order in orders.items() if order.get('viewer') == current_user.id}
        print(viewer_orders)
        return render_template('my_orders.html', viewer_orders=viewer_orders)
    else:
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('home'))

@app.route('/admin/manage_items', methods=['GET', 'POST'])
@login_required
def manage_items():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.')
        return redirect(url_for('home'))

    items = load_items()

    if request.method == 'POST':
        item_id = request.form['item_id']
        name = request.form['name']
        price = request.form['price']

        items[item_id] = {'name': name, 'price': price}
        save_items(items)
        flash('Item updated/added successfully.')

    return render_template('manage_items.html', items=items)
    
if __name__ == '__main__':
    app.run(debug=True)