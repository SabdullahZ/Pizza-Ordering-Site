from flask import Flask, render_template
from db import initialize_db
from routes import api_bp

app = Flask(__name__)

# MongoDB configuration
app.config['MONGODB_SETTINGS'] = {
    'db': 'PIZZA',
    'host': 'localhost',
    'port': 27017
}

# Initialize DB
initialize_db(app)

# Register API Blueprint
app.register_blueprint(api_bp)

# Routes for rendering HTML pages
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
