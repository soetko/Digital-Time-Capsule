from flask import Flask, render_template, redirect, url_for
from forms import LoginForm, SignupForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        # process form here
        return redirect(url_for('login'))
    return render_template("signup.html", form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # process form here        
        return "You have successfully logged in."    
    return render_template("login.html", form=form)

if __name__ == "__main__":
    app.run(debug=True)
