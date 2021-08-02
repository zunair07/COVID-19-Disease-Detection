from flask import Flask, render_template, flash, redirect, request, url_for, session, jsonify
from flask_mysqldb import MySQL, MySQLdb
import bcrypt
import re, os, cv2
from werkzeug.utils import secure_filename
import keras
from keras.models import load_model
from keras.preprocessing import image
import numpy as np


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Mysqlroot1234'
app.config['MYSQL_DB'] = 'covide_detector_webapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


patient_data = []

app.config['IMAGE_UPLOADS'] = 'E:\\Covid_Project\\static\\upload_xray'




 
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])


app.config['SECRET_KEY'] = 'coviddetails'

data_mean = 134.2425880582117
data_std = 64.23012464908116

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def covid_prediction(file_location):
    binary_cls_Best_Model = load_model("Covid_Detection_Model-v6.h5")
    img = image.load_img(file_location, target_size=(256,256),color_mode='grayscale')
    if not img:
        return 'Wrong Image'
    else:
        img = image.img_to_array(img)
        #img = np.expand_dims(img, axis=0)
        img = ((img - data_mean) / data_std)
        img = img.reshape(-1,256,256,1)
        p = binary_cls_Best_Model.predict(img)
        res = np.round(p)
        if res[0][0]==1:
            result = 'Normal'
        else:
            result = 'Positive'
        
        return result


@app.route('/')
def home_page():
    return render_template('home.html')



@app.route('/patientdetails', methods=['GET', 'POST'])
def index():
    
    if request.method == 'POST':
        cNic = request.form['cnic']
        patientname = request.form['name']
        age = request.form['age']
        contactnum = request.form['contactnum']
        gender = request.form.get('gender')
        try: 
            digit = int(patientname)

        
            if type(digit) == int:
                return jsonify({'name_error' : '*Please enter your correct name '})
        except ValueError:
            if not cNic:
                return jsonify({'cnic_error' : '*CNIC Field Cannot be Null!'})
            
            regex = '^[0-9]{5}-[0-9]{7}-[0-9]$'
            
            if not (re.search(regex, cNic)):
                return jsonify({'cnic_error' : '*CNIC No must follow the XXXXX-XXXXXXX-X format!'})
            
            if int(age)<10 or int(age)>120:
                return jsonify({'age_error' : '*Age Should be greater than 10 or less than 120 years .'})

            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT * FROM patients where cnic=%s", (cNic,))
            user = cur.fetchone()
            cur.close()

            if user:
                return jsonify({'cnic_error' : "*Patient Already Exist, \n Please click 'Patient Already Exist' Button"})
                    

            if gender=="None":
                return jsonify({'gen_error' : '*Please Select Your Gender!'})
        
            patient_data.append(cNic)
            patient_data.append(patientname)
            patient_data.append(age)
            patient_data.append(contactnum)
            patient_data.append(gender)

            #print(patient_data)
            return "success"
            
        
            
        

    if session:
        return render_template("index.html")
        
    
    else:
        err = 'Login Required To Get Prediction!'
        return render_template("login.html", err=err)


@app.route('/file_upload', methods=['GET', 'POST'])
def file_upload():
    if request.method == "POST":
        file = request.files['img']


        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['IMAGE_UPLOADS'], filename))
            
            file_type = os.path.splitext(os.path.abspath(filename))[-1].lower()
            newfilename_location = app.config['IMAGE_UPLOADS']+'\\'+patient_data[0]+file_type
            os.rename(os.path.join(app.config['IMAGE_UPLOADS'], filename), newfilename_location )
            
    
            patient_data.append(newfilename_location)
            print(patient_data)
            again = "Predict Another"
            prediction = covid_prediction(newfilename_location)

            patient_data.append(prediction)
            patient_data.append(session['userid'])
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO patients (cNic,patientname,age,contactnum,gender,image, prediction, userID) VALUES (' + ', '.join(['%s' for i in range(len(patient_data))]) + ')', patient_data)
            mysql.connection.commit()
            cur.close()
            del patient_data[:]
            
            if  prediction == 'Normal':
               
                return render_template('file_upload.html',again=again, nor=prediction)

            elif prediction == 'Positive':
                
                return render_template('file_upload.html',again=again, pos=prediction)

            else:
                return render_template('file_upload.html', err=covid_prediction(file_location))

            

        else:
           
            err = "Only JPG/JPEG & PNG Image Format are Allowed"
            #print(patient_data)
            return render_template('file_upload.html',err=err)
            



    if( len(patient_data) == 5):
        return render_template('file_upload.html')

    else:
        del patient_data[:]
        return render_template('index.html')
    

@app.route('/patientexist', methods=['GET', 'POST'])
def fileupload_exist():
    if request.method == 'POST':
        cNic = request.form['cnic']
        file = request.files['img']

        regex = '^[0-9]{5}-[0-9]{7}-[0-9]$'
        
        if not (re.search(regex, cNic)):
            return render_template('fileupload_exist.html', cnic_err = '*CNIC No must follow the XXXXX-XXXXXXX-X format!')

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM patients where cNic=%s", (cNic,))
        user = cur.fetchone()
        cur.close()

        if not user:
                return render_template('fileupload_exist.html', cnic_err = "Patient Does Not Exist, \n Please Save Patient's Detail on Previous Page" )

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['IMAGE_UPLOADS'], filename))
            
            file_type = os.path.splitext(os.path.abspath(filename))[-1].lower()

            if os.path.exists(app.config['IMAGE_UPLOADS']+'\\'+cNic+file_type):
                os.remove(app.config['IMAGE_UPLOADS']+'\\'+cNic+file_type)

            newfilename_location = app.config['IMAGE_UPLOADS']+'\\'+cNic+file_type
            os.rename(os.path.join(app.config['IMAGE_UPLOADS'], filename), newfilename_location )
           
    

            prediction = covid_prediction(newfilename_location)
            
      

            cur = mysql.connection.cursor()
            sql = "UPDATE patients SET image= %s , prediction= %s, userID= %s WHERE cNic = %s"
            val = (newfilename_location, prediction, session['userid'], cNic)
            cur.execute(sql,val)
            mysql.connection.commit()
            cur.close()

            if prediction == 'Normal':
                
                return render_template('fileupload_exist.html', nor=prediction)

            elif prediction == 'Positive':
        
                return render_template('fileupload_exist.html', pos=prediction)

            else:
                return render_template('fileupload_exist.html', err ="something went wrong!")

            

           
        
        else:
            err = "Only JPG/JPEG & PNG Image Format are Allowed"
            return render_template('fileupload_exist.html',err=err)

        
    else:
        return render_template('fileupload_exist.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['cpassword']
        recovery_question = request.form['recovery_ans'].lower()

  

        if name.isdigit():
            return jsonify({'name_error' : '*Please enter correct Name!'})
        

        
    
        
        if recovery_question.isdigit():
            return jsonify({'recovery_ans_error' : '*Please enter correct answer, it will help you to reset your password!'})
        
        regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

        if not (re.search(regex, email)):
            return jsonify({'email_error' : "*Invalid Email, Email No must follow the 'abc@xyz.com' format!"})
        
        if confirm_password != password:
            return jsonify({'cpassword_error' : '*Password Does Not Matched!'})

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM login_info where email=%s", (email,))
        user = cur.fetchone()
        cur.close()

        if user:
            return jsonify({'email_error' : '*User Already Exists!'})
            
            
        else:
            hash_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            hash_question = bcrypt.hashpw(recovery_question.encode('utf-8'), bcrypt.gensalt())

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO login_info (Name,Email,Password, RecoveryQ) VALUES (%s,%s,%s,%s)",(name, email, hash_password, hash_question))
            mysql.connection.commit()
            #return redirect(url_for('login'))
            return render_template("login.html")

    else:
        return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method == "POST":
        uemail = request.form['email']
        password = request.form['password'].encode('utf-8')

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM login_info where Email=%s", (uemail,))
        user = cur.fetchone()
        cur.close()

        if user:
                  
            if bcrypt.hashpw(password, user['Password'].encode('utf-8')) == user['Password'].encode('utf-8'):
                session['userid'] = user['userID']
                session['name'] = user['Name']
                session['email'] = user['Email']
                return render_template('home.html')

            else:
                return jsonify({'password_error' : '*Invalid Password'})

        else:
            return jsonify({'email_error' : '*User Does Not Exists!'})

    

        if not email:
            return jsonify({'email_error' : '*Please Enter Email!'})
            


        regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

        if not (re.search(regex, email)):
            return jsonify({'email_error' : '*Invalid Email'})
        

        if not password:
            return jsonify({'password_error' : '*Password Field Cannot be Null!'})
        
        
                
    elif request.method == 'GET':
        return render_template("login.html")
        


@app.route('/forgetpwd', methods=['GET', 'POST'])
def forgetpwd():
    if request.method == "POST":
        email = request.form['email']
        answer = request.form['recovery_ans'].lower()
        password = request.form['password']
        confirm_password = request.form['cpassword']

        regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

        if not (re.search(regex, email)):
            return jsonify({'email_error' : "*Invalid Email, Email No must follow the 'abc@xyz.com' format!"})

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
       
        cur.execute("SELECT * FROM login_info where Email=%s", (email,))
        user = cur.fetchone()
        cur.close()

        if user:
            hash_ans = answer.encode('utf-8')

            if bcrypt.hashpw(hash_ans, user['RecoveryQ'].encode('utf-8')) == user['RecoveryQ'].encode('utf-8'):
                
                if confirm_password != password:
                    return jsonify({'cpassword_error' : '*Password Does Not Matched!'})

                else:

                    hash_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

                    cur = mysql.connection.cursor()
                    sql = "UPDATE login_info SET Password = %s WHERE email = %s"
                    val = (hash_password, email)
                    cur.execute(sql,val)
                    mysql.connection.commit()
                    return render_template("login.html")
            else:
                return jsonify({'recovery_ans_error' : "*Sorry, Your Answer Does Not Matched!"})

        else:
            return jsonify({'email_error' : "*User Does Not Exist, Please Register First!"})

    else:
        return render_template("forgetpwd.html")


@app.route('/logout')
def logout():
    session.clear()
    return render_template("home.html")
    

@app.route('/ourteam')
def ourteam():
    return render_template('ourteam.html')


if __name__ == "__main__":
    app.run(debug=True)
