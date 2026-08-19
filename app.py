"""
ARIRANG Fan Site + Shop - Flask College Project
------------------------------------------------
Info section: album facts, tracklist
Shop section: merch catalog with login, cart, checkout

Run with:  python app.py
Then open: http://127.0.0.1:5000
"""

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------------------------------------------------
# APP SETUP
# ---------------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret-key-later'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///arirang.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


# ---------------------------------------------------------
# DATABASE MODELS
# ---------------------------------------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    is_title_track = db.Column(db.Boolean, default=False)
    spotify_id = db.Column(db.String(50))


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Photocard / Light Stick / Album
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(300))
    emoji = db.Column(db.String(10), default='🎵')


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    product = db.relationship('Product')


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    total = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # price at time of purchase


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------------------------------------------------
# INFO ROUTES
# ---------------------------------------------------------
@app.route('/')
def home():
    tracks = Track.query.order_by(Track.number).all()
    return render_template('home.html', tracks=tracks)


@app.route('/about')
def about():
    return render_template('about.html')


# ---------------------------------------------------------
# AUTH ROUTES
# ---------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already taken. Try another.')
            return redirect(url_for('register'))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('shop'))
        else:
            flash('Invalid username or password.')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


# ---------------------------------------------------------
# SHOP ROUTES
# ---------------------------------------------------------
@app.route('/shop')
def shop():
    category = request.args.get('category')
    if category:
        products = Product.query.filter_by(category=category).all()
    else:
        products = Product.query.all()
    categories = ['Photocard', 'Light Stick', 'Album']
    return render_template('shop.html', products=products, categories=categories, active=category)


@app.route('/add_to_cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    existing = CartItem.query.filter_by(
        user_id=current_user.id, product_id=product_id
    ).first()

    if existing:
        existing.quantity += 1
    else:
        db.session.add(CartItem(user_id=current_user.id, product_id=product_id))

    db.session.commit()
    flash('Added to cart!')
    return redirect(url_for('shop'))


@app.route('/cart')
@login_required
def cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in items)
    return render_template('cart.html', items=items, total=total)


@app.route('/remove_from_cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()

    if not items:
        flash('Your cart is empty.')
        return redirect(url_for('shop'))

    total = sum(item.product.price * item.quantity for item in items)

    if request.method == 'POST':
        full_name = request.form['full_name']
        address = request.form['address']
        city = request.form['city']
        postal_code = request.form['postal_code']

        new_order = Order(
            user_id=current_user.id,
            full_name=full_name,
            address=address,
            city=city,
            postal_code=postal_code,
            total=total
        )
        db.session.add(new_order)
        db.session.flush()  # gets new_order.id before commit

        for item in items:
            db.session.add(OrderItem(
                order_id=new_order.id,
                product_name=item.product.name,
                quantity=item.quantity,
                price=item.product.price
            ))
            db.session.delete(item)  # clear the cart

        db.session.commit()
        return redirect(url_for('order_confirmation', order_id=new_order.id))

    return render_template('checkout.html', items=items, total=total)


@app.route('/order_confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        return redirect(url_for('home'))
    return render_template('order_confirmation.html', order=order)


@app.route('/orders')
@login_required
def orders():
    my_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=my_orders)


# ---------------------------------------------------------
# SEED DATA (real tracklist + sample merch)
# ---------------------------------------------------------
def seed_data():
    if Track.query.count() == 0:
        tracklist = [
            ("Body to Body", "2rKkfc4VZ74FQDc1FF1Zo6"),
            ("Hooligan", "20dAJsyno9ZoBLJtqgQnUI"),
            ("Aliens", "5tg21NdePCn5m8F9BXOEeJ"),
            ("FYA", "0KmrKOdScRDVYwWS8hkkdv"),
            ("2.0", "3bmpXHVie1GTy37OkXJ7Vc"),
            ("No. 29", "3plyGpDgzfrnZbpElpfioV"),
            ("SWIM", "68lbSrXDORS51pmyjZv712"),
            ("Merry Go Round", "3VegC0PZiHjGxb80DER8XU"),
            ("NORMAL", "4B4Q7zfd0aHcuhQBfCRnH5"),
            ("Like Animals", "2IFND3phjzIG1RcPnHh2hP"),
            ("they don't know 'bout us", "0b61A7v9agI08BG21jJPQ9"),
            ("One More Night", "6s3w7SUVtmm68Bw5KrKMh0"),
            ("Please", "1XpVhaI4HzWrhRWIpdfyJB"),
            ("Into the Sun", "1ZNolq7VI7efGlh2hb2VVr"),
        ]
        for i, (title, spotify_id) in enumerate(tracklist, start=1):
            db.session.add(Track(
                number=i, title=title, spotify_id=spotify_id,
                is_title_track=(title == "SWIM")
            ))
        db.session.commit()
        print("Tracklist seeded.")

    if Product.query.count() == 0:
        members = ["RM", "Jin", "Suga", "J-Hope", "Jimin", "V", "Jung Kook"]
        products = []
        for m in members:
            products.append(Product(
                name=f"{m} Photocard", category="Photocard", price=4.99,
                emoji="🃏", description=f"Official ARIRANG era photocard — {m}."
            ))
        products.append(Product(
            name="Official Light Stick Ver. 4", category="Light Stick", price=59.99,
            emoji="💡", description="Bluetooth-connected fan light stick, latest version."
        ))
        products.append(Product(
            name="ARIRANG - Rooted in Korea Ver.", category="Album", price=24.99,
            emoji="💿", description="CD version with photobook themed around heritage."
        ))
        products.append(Product(
            name="ARIRANG - Rooted in Music Ver.", category="Album", price=24.99,
            emoji="💿", description="CD version focused on the album's musical journey."
        ))
        products.append(Product(
            name="ARIRANG - Living Legend Ver.", category="Album", price=27.99,
            emoji="💿", description="Special collector's CD version."
        ))
        products.append(Product(
            name="ARIRANG - Travel Tag CD Box Set", category="Album", price=39.99,
            emoji="🧳", description="Boxed set with travel-tag themed packaging."
        ))
        db.session.bulk_save_objects(products)
        db.session.commit()
        print("Sample merch seeded.")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True)
