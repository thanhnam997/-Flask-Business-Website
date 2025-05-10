from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import or_

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///business_site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Contact model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Contact {self.name}>'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        # Create a new Contact instance
        new_contact = Contact(name=name, email=email, message=message)
        
        try:
            # Add to database and commit
            db.session.add(new_contact)
            db.session.commit()
            flash('Thank you for your message! We will get back to you soon.', 'success')
        except Exception as e:
            # In case of error, roll back
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
        
        return redirect(url_for('contact'))
        
    return render_template('contact.html')

# Add a route to view all contact submissions (admin page)
@app.route('/admin/contacts')
def view_contacts():
    # In a real app, this should be protected with authentication
    contacts = Contact.query.order_by(Contact.date_submitted.desc()).all()
    return render_template('admin_contacts.html', contacts=contacts)

# Create database tables before running the app
# The following code works with all Flask versions
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/admin/search')
def search_contacts():
    query = request.args.get('q', '')
    if query:
        contacts = Contact.query.filter(
            or_(
                Contact.name.contains(query),
                Contact.email.contains(query),
                Contact.message.contains(query)
            )
        ).order_by(Contact.date_submitted.desc()).all()
    else:
        contacts = []

    return render_template('search_contacts.html', contacts=contacts, query=query)
