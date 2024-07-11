from flask import Blueprint, render_template, request, flash

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        # Here you would typically process the form data, like sending an email or saving to a database
        flash('Thank you for your message! We will get back to you soon.', 'success')

    content = render_template('contact_content.html')
    return render_template('base.html', title="Contact Us", content=content)