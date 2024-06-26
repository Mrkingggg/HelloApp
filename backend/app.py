from datetime import datetime
from flask import Flask, jsonify, request,session
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token,jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash,check_password_hash
from flask_marshmallow import Marshmallow
from queue import Queue
from flask_cors import CORS

import threading
import uuid
# from flask_cors import CORS

# 在创建 Flask 应用后立即添加


app = Flask(__name__)
CORS(app)

api = Api(app)
#connect to my database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root1234@localhost:3306/HealthApp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = '2fdbf97d3094c3c8896e173f16c55fcb'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
ma  = Marshmallow(app) 
report_queue = Queue() # report queue
reports_status = {} 
notification_queue = Queue()
# medium tables:

rolesmap = db.Table('rolesmap', 
                    db.Column('userId',db.Integer, db.ForeignKey('users.userId'), primary_key=True),
                    db.Column('roleId',db.Integer, db.ForeignKey('role.roleId'), primary_key=True)
                    )

# database models: 
class Measurements(db.Model):
    __tablename__ = 'measurements'
    MeasurementId = db.Column(db.Integer, primary_key=True)
    deviceId  = db.Column(db.Integer, db.ForeignKey('device.deviceId'))
    userId = db.Column(db.Integer, db.ForeignKey('users.userId'))
    
class Users(db.Model):
    __tablename__ = 'users'
    userId = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(150),unique = True, nullable=False)
    email = db.Column(db.String(150), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    fullname = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.Enum("female","male","other"))
    roles = db.relationship('Role', secondary=rolesmap, backref=db.backref('users', lazy='dynamic'))
    measurements = db.relationship('Measurements', backref='user', lazy=True)

class Role(db.Model):
    __tablename__ = 'role'
    roleId = db.Column(db.Integer, primary_key = True)
    rolename = db.Column(db.Enum('patient','doctor','admin'), unique=True, nullable=False)

class Device(db.Model):
    __tablename__ = 'device'
    deviceId = db.Column(db.Integer, primary_key = True)
    manufactor = db.Column(db.String(255), nullable = False)
    devType = db.Column(db.String(50),nullable = False)
    unit = db.Column(db.String(50),nullable=False)
    measurements = db.relationship('Measurements', backref='device', lazy=True)
    value = db.Column(db.Numeric(10, 2), nullable=True) 
    measuretime = db.Column('measuretime', db.DateTime, nullable=False, server_default=db.func.current_timestamp())

class DeviceSchema(ma.SQLAlchemyAutoSchema):    # for nested json
    class Meta:
        model = Device
        include_fk = True

class Appointment(db.Model):
    __tablename__ = 'appointments'
    appointmentId = db.Column(db.Integer, primary_key=True)
    patientId = db.Column(db.Integer, db.ForeignKey('users.userId'))
    doctorId = db.Column(db.Integer, db.ForeignKey('users.userId'))
    appointmentTime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.Enum('scheduled', 'completed', 'cancelled'), default='scheduled')



class MeaSchema(ma.SQLAlchemyAutoSchema):   # for nested json
    class Meta:
        model = Measurements
    posts = ma.Nested(DeviceSchema(many=True))

# db.create_all()

# class HelloWorld(Resource):
#     def get(self):
#         return jsonify({"message": "hello world"})

# api.add_resource(HelloWorld, '/hello')

@app.route('/api/users/hello', methods=['GET'])
def hello():
    return jsonify({"message":"hello world"}),200
    
@app.route('/api/users/add', methods=['POST'])
def add_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    dob  = data.get('dob')
    fullname = data.get('fullname')
    password = data.get('password')
    gender = data.get('gender')
    role_ids = data.get('role_ids',[])

    if not all([username, email, dob, fullname, password, gender, role_ids]):
        return jsonify({"error":"Missing information"}),400
    
    if Users.query.filter_by(username=username).first():
        return jsonify({"error":"Username already exists"}),400
    
    hash_psw = generate_password_hash(password)

    try:
        dob_parse = datetime.strptime(dob, '%Y-%m-%d').date()
        user = Users(username=username, email=email, dob=dob_parse, fullname=fullname, password = hash_psw, gender=gender)
        db.session.add(user)
        db.session.flush() # assign id ?
        for role_id in role_ids:
          role = Role.query.get(role_id)
          if role:
            user.roles.append(role)

        db.session.commit()
        return jsonify({"message": "User added successfully", "userId": user.userId}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/users/changeRole', methods=['PUT'])
def chg_role():
    data = request.get_json()
    userId = data.get('userId')
    newRoles = data.get('newRoles',[])
    if not all([userId, newRoles]):
        return jsonify({"bad requests":"missing components"}),400
    if not Users.query.filter(userId = userId).first():
        return jsonify({"bad request":"user does not exist"}),400
    
    try:
        usr = Users.query.filter(userId = userId).first()
        usr.roles=[]
        for role_id in newRoles:
            roleName = Role.query.get(role_id)
            if roleName:
                usr.roles.append(roleName)
        db.session.commit()
        return jsonify({"Success":"complete role changing!"}),200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}),500  # error in server

def process_notify_queue():
    while not notification_queue.empty():
        noti_task = notification_queue.get()
        userId, msg = noti_task['userId'], noti_task['msg']
        print(f"Send notification to user: {userId}: {msg}"),200
        
        notification_queue.task_done()


@app.route('/api/notifications/send', methods=['POST'])
def notify():
    data = request.get_json()
    userId = data.get('userId')
    msg = data.get('msg')
    if not userId or not Users.query.filter(userId = userId).first():
        return jsonify({"bad request":"invalid userId"}),400
    
    notification_queue.put({'userId': userId, 'msg': msg})

    return jsonify({"message": "Notification is being processed."}), 202



def process_report_queue():
    with app.app_context():
        while not report_queue.empty():
            userId = report_queue.get()
            try:
                res = Measurements.query.get_or_404(userId)
                res_schema = MeaSchema()
                report_data = res_schema.dump(res)

                report_id = str(uuid.uuid4())
                reports_status[report_id] = {"status": "completed", "data": report_data}

                print(f"userId: {userId} 's report: {report_data}")
            except Exception as e:
                print(f"error when generating report: {e}")
            finally:
                report_queue.task_done()

def start_background_thread():
    t_repo = threading.Thread(target=process_report_queue)
    t_repo.daemon = True
    t_repo.start()

    t_noti = threading.Thread(target=process_notify_queue)
    t_noti.daemon = True
    t_noti.start()
start_background_thread()


@app.route('/api/reports/gen/<int:userId>', methods=['GET'])
def repo_gen(userId):
    if not Measurements.query.filter_by(userId=userId).first():
        return jsonify({"bad request": "user does not exist."}), 400

    report_queue.put(userId)
    report_id = str(uuid.uuid4())  # unique report id
    reports_status[report_id] = {"status": "in progress"}

    return jsonify({"message": "Report generation in progress.", "reportId": report_id}),202


@app.route('/api/reports/status/<reportId>', methods=['GET'])
def report_status(reportId):
    status_info = reports_status.get(reportId)
    if not status_info:
        return jsonify({"error": "Report ID not found."}), 404

    if status_info["status"] == "completed":
        return jsonify({"status": "completed", "data": status_info["data"]}), 200
    else:
        return jsonify({"status": "in progress"}),202


    # devs = Device.query.filter(deviceId = res.deviceId).all() # select all device ids for one measurement
    # patient = Users.query.filter(userId = userId).first()  # select patient from users by userId
    
    # pname = patient.username  # report needed info.
    # dob = patient.dob

    # for dev in devs:
    #     devType = dev.devType  
    #     unit =res.unit
    #     value = res.value
    #     mtime = res.measuretime

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    inputpsw = data.get('password')

    if Users.query.get_or_404(username=username):
        return jsonify({"bad request":"invalid username"}),400

    user = Users.query.get(username=username)
    hashpsw = user.password
    check = check_password_hash(hashpsw, inputpsw)

    if not check:
        return jsonify({"error":"incorrect password"}),401
    if check:
        return jsonify({"message":"Login Successfully"}),200 # no jwt-verify temporarily

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message":"Successfully logout"}),200
    

if __name__ == '__main__':
    # db.create_all()
    app.run(debug=True, port = 5050) # default port: 5000