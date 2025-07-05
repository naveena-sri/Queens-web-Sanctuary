from flask import Flask, render_template,request, jsonify
from flask_mail import Mail, Message

app = Flask(__name__)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'navee20052005@gmail.com' # Your email
app.config['MAIL_PASSWORD'] = 'hgzk benl edxx bvog'  # Your email password (use an app password for Gmail)
app.config['MAIL_DEFAULT_SENDER'] = 'naveenapandi20@gmail.com'

mail = Mail(app)
@app.route('/')
def index():
    return render_template('page2.html')

@app.route('/send-email', methods=['POST'])
def send_email():
    try:
        data = request.get_json()

        patient_email = data['email']
        session = data['session']
        availability = data['availability']
        token = data['token']
        doctor_email = data['receiverEmail']

        # Send confirmation email to the patient
        patient_msg = Message("Appointment Confirmation", recipients=[patient_email])
        patient_msg.body = f"""
        Dear Patient,

        Your appointment has been successfully booked! 🎉

        📅 Date: {availability}  
        🕒 Session: {session}  
        🎟️ Token Number: {token}

        You will receive a reminder email before your appointment.

        Take care! 💙
        """
        mail.send(patient_msg)

        # Send appointment details to the doctor
        doctor_msg = Message("New Appointment Scheduled", recipients=[doctor_email])
        doctor_msg.body = f"""
        Hello Doctor,

        A new appointment has been booked!

        📧 Patient Email: {patient_email}  
        📅 Date: {availability}  
        🕒 Session: {session}  
        🎟️ Token Number: {token}

        Please confirm or manage the appointment as needed.

        Best regards,  
        Appointment System
        """
        mail.send(doctor_msg)

        return jsonify({"message": "Emails sent to patient and doctor successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
