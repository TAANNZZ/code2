from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class NGO(db.Model):
    __tablename__ = 'ngo'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(6), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)

    users = db.relationship('User', backref='ngo', lazy=True)

class User(db.Model):
    __tablename__ = 'user'
    phone_number = db.Column(db.String(10), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(500), nullable=False)
    food_amount = db.Column(db.Integer, nullable=False)
    type_of_food = db.Column(db.String(200), nullable=False)

    
    pincode = db.Column(db.String(6), db.ForeignKey('ngo.pincode'), nullable=False)  

with app.app_context():
    db.create_all()
    if not NGO.query.first(): 
        ngo1 = NGO(name="Food Bank", pincode="751001", phone_number="9876543210", email="foodbank@gmail.com")
        ngo2 = NGO(name="Helping Hands", pincode="751002", phone_number="9876500000", email="helpinghands@gmail.com")
        db.session.add_all([ngo1, ngo2])
        db.session.commit()

@app.route('/api/register',methods=['POST'])
def register_user():
     data=request.get_json()
     if not data:
          return jsonify({"message":"no data received"}),400
     required_fields = ["first_name", "last_name", "phone_number", "email", 
                       "address", "food_amount", "type_of_food", "pincode"]
     for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"message": f"Missing field: {field}"}), 400


     first_name = data["first_name"]
     last_name = data["last_name"]
     phone_number =data['phone_number'] 
     email=data['email']
     address=data['address']
     type_of_food = data['type_of_food']
     pincode=data['pincode']
     food_amount = data['food_amount']
     try:
            food_amount = int(food_amount)
     except ValueError:
            return jsonify({"message": "food_amount must be a number"}), 400

     org_count = NGO.query.filter_by(pincode=pincode).count()

     if org_count > 0:
          try:
                user = User(
                    phone_number=phone_number,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    address=address,
                    food_amount = food_amount,
                    type_of_food= type_of_food,
                    pincode=pincode
                )

                db.session.add(user)
                db.session.commit()
                return jsonify({"message" : f"User added! There are {org_count} organisations in your area."}), 201
          except Exception as e:
                db.session.rollback()
                if "UNIQUE constraint failed" in str(e):
                    return jsonify({"message": "Duplicate email or phone number"}), 409
                return jsonify({"message": "Unexpected error", "error": str(e)}), 500


if __name__=="__main__":
    app.run(debug=True)



