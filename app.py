import re
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Medical knowledge base
MEDICAL_RESPONSES = {
    # Respiratory Conditions

    r'(?i).*(how are you|hi|hello).*': [
        "Hello, I'm a medical assistant chatbot. I can help provide general health information. What symptoms or health concerns do you have?",
        "Hello! I'm here to offer basic medical guidance. Please describe your health question."
    ] ,

    r'(?i).*(covid|coronavirus).*': [
        "COVID-19 symptoms include fever, dry cough, fatigue, loss of taste/smell, and shortness of breath. Isolate yourself, wear a mask, and get tested.",
        "If you test positive, follow CDC guidelines: rest, stay hydrated, monitor symptoms, and contact your healthcare provider if breathing difficulties occur."
    ],
    r'(?i).*(pneumonia|lung infection).*': [
        "Pneumonia can be bacterial or viral. Symptoms include high fever, chills, persistent cough with phlegm, chest pain, and difficulty breathing.",
        "Seek immediate medical attention if you have severe symptoms, high fever, or persistent chest pain. Antibiotics may be required for bacterial pneumonia."
    ],
    r'(?i).*(asthma|breathing difficulty).*': [
        "Asthma symptoms include wheezing, chest tightness, shortness of breath, and persistent cough. Use prescribed inhalers and avoid known triggers.",
        "During an asthma attack: use quick-relief inhaler, sit upright, and take slow, steady breaths. Seek emergency care if symptoms don't improve."
    ],

    # Cardiovascular Conditions
    r'(?i).*(heart attack|chest pain).*': [
        "Heart attack warning signs: chest discomfort, pain radiating to arm/jaw, shortness of breath, cold sweat, nausea, lightheadedness.",
        "EMERGENCY ACTION: Call 911 immediately if you suspect a heart attack. Do not drive yourself. Chew aspirin if available and wait for medical help."
    ],
    r'(?i).*(high blood pressure|hypertension).*': [
        "High blood pressure often has no symptoms. Regular monitoring is crucial. Manage through diet, exercise, stress reduction, and prescribed medications.",
        "Risk factors include obesity, salt intake, stress, age, and family history. Consult a doctor for personalized management strategies."
    ],

    # Neurological Conditions
    r'(?i).*(migraine|severe headache).*': [
        "Migraines involve intense, throbbing pain, often with light/sound sensitivity, nausea. Triggers include stress, hormonal changes, certain foods.",
        "Management: identify triggers, rest in dark room, use prescribed medications, apply cold compress, stay hydrated. Consult neurologist for persistent migraines."
    ],
    r'(?i).*(stroke|stroke symptoms).*': [
        "FAST stroke recognition: Face drooping, Arm weakness, Speech difficulty, Time to call emergency services.",
        "Immediate medical attention is critical. Symptoms include sudden numbness, confusion, trouble speaking, vision problems, severe headache."
    ],

    # Digestive Conditions
    r'(?i).*(acid reflux|gerd).*': [
        "GERD symptoms: heartburn, chest pain, difficulty swallowing, chronic cough. Avoid trigger foods, eat smaller meals, don't lie down after eating.",
        "Treatment includes lifestyle changes, over-the-counter antacids, and prescription medications. Persistent symptoms require medical consultation."
    ],
    r'(?i).*(food poisoning|stomach flu).*': [
        "Symptoms include vomiting, diarrhea, abdominal pain, fever. Stay hydrated, rest, eat bland foods. Oral rehydration solutions are crucial.",
        "Seek medical help if symptoms persist over 3 days, signs of severe dehydration, high fever, or bloody stools appear."
    ],

    # Mental Health
    r'(?i).*(anxiety|panic attack).*': [
        "Anxiety symptoms: excessive worry, restlessness, rapid heartbeat, difficulty concentrating. Breathing exercises, therapy, and medication can help.",
        "Techniques: deep breathing, mindfulness, regular exercise. Professional help recommended for persistent or debilitating anxiety."
    ],
    r'(?i).*(depression|feeling sad).*': [
        "Depression involves persistent sadness, loss of interest, changes in sleep/appetite. Professional help is crucial for proper diagnosis and treatment.",
        "Seek support from mental health professionals. Treatment may include therapy, medication, lifestyle changes, and support groups."
    ],

    # General Health
    r'(?i).*(fever|temperature).*': [
        "Fever is a body temperature above 100.4°F (38°C). Monitor closely. Use fever reducers, stay hydrated, rest.",
        "Seek medical attention for infants, elderly, or if fever exceeds 103°F, lasts more than three days, or is accompanied by severe symptoms."
    ],
    r'(?i).*(diabetes|blood sugar).*': [
        "Diabetes types include Type 1, Type 2, and gestational. Symptoms: frequent urination, increased thirst, unexplained weight loss.",
        "Management involves diet, exercise, monitoring blood sugar, and medication. Regular check-ups with an endocrinologist are essential."
    ]
    
}

# Enhanced Fallback Responses
FALLBACK_RESPONSES = [
    "I can provide general health information, but I'm not a substitute for professional medical advice.",
    "For specific or complex medical concerns, please consult a healthcare professional directly.",
    "My responses are informational. Always seek personalized medical guidance from a qualified doctor.",
    "I can offer general health insights, but medical diagnosis requires professional examination.",
    "Health concerns vary individually. A healthcare provider can offer personalized assessment and treatment."
]


def find_best_response(user_message):
    """Find the most appropriate response based on message matching."""
    for pattern, responses in MEDICAL_RESPONSES.items():
        if re.search(pattern, user_message):
            return responses[0]  # Return first matching response
    return FALLBACK_RESPONSES[0]  # Default fallback response

@app.route('/medx')
def medx():
    """Render the chatbot interface."""
    return render_template('medx.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests."""
    user_message = request.json.get('message', '')
    response = find_best_response(user_message)
    return jsonify({'response': response})

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    tracking_data = db.Column(db.Text, nullable=True)  # To store user-specific tracking data

# Create the database
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(username=username).first():
            return render_template('signup.html', error="Username already exists")
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', username=user.username, tracking_data=user.tracking_data)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)