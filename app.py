from flask import Flask, render_template
from models.database import db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lajor_coffee.db"
db.init_app(app)

@app.route("/")
def home():
    return render_template("home.html")


from flask import Flask, render_template, redirect, url_for, request, flash
from models.database import db, User
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lajor_coffee.db"
app.config["SECRET_KEY"] = "your_secret_key_here"

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route utama
@app.route("/")
def home():
    return render_template("home.html")

# Route login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  # Untuk demo, plaintext; gunakan hash di produksi!
            login_user(user)
            flash("Login berhasil!", "success")
            return redirect(url_for("home"))
        else:
            flash("Username atau password salah.", "danger")
    return render_template("login.html")

# Route logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Kamu telah logout.", "info")
    return redirect(url_for("home"))

if __name__ == "__main__":
    # Pastikan database sudah dibuat, misalnya dengan shell Flask atau perintah db.create_all()
    app.run(debug=True)
    
# Route Pemesanan

import json
from models.database import MenuItem, Order

# Route untuk menampilkan menu dan form pemesanan
@app.route("/order", methods=["GET", "POST"])
def order():
    if request.method == "POST":
        customer_name = request.form.get("customer_name")
        # Misal: item ids dikirim sebagai list string, konversi ke list
        selected_items = request.form.getlist("menu_item")
        # Ambil harga tiap item dan hitung total
        items = MenuItem.query.filter(MenuItem.id.in_(selected_items)).all()
        total_price = sum(item.price for item in items)
        order_data = Order(
            customer_name=customer_name,
            items=json.dumps(selected_items),  # Simpan sebagai JSON
            total_price=total_price
        )
        db.session.add(order_data)
        db.session.commit()
        flash("Pesanan berhasil dikirim!", "success")
        return redirect(url_for("order"))
    else:
        menu_items = MenuItem.query.all()
        return render_template("order.html", menu_items=menu_items)

    
# Pastikan untuk membuat/memperbarui database dengan menjalankan:
with app.app_context():
    db.create_all()

# Running Command
if __name__ == "__main__":
    app.run(debug=True, port=5001)

