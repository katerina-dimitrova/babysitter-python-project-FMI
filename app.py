from flask import Flask, render_template
from models import Babysitter
from logic import filter_by_city, get_top_rated_sitters

app = Flask(__name__)

MOCK_SITTERS = [
    Babysitter(1, "Maria Petrova", "Sofia", 15.50, 5, "I love children!", 4.8, 12),
    Babysitter(2, "Ivana Ivanova", "Plovdiv", 12.00, 2, "Student of pedagogy", 4.5, 5),
    Babysitter(3, "Elena Georgieva", "Varna", 20.00, 7, "Experienced nanny", 4.9, 20),
]

@app.route('/')
def index():
    top_sitters = get_top_rated_sitters(MOCK_SITTERS)
    return render_template('index.html', sitters=top_sitters)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return "Error occurred. Please try again later.", 500

if __name__ == '__main__':
    app.run(debug=True)