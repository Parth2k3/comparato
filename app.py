from flask import Flask, render_template, request, session, redirect, url_for
from functools import wraps
from database import login_user, uploadImages, getimages, incScore, signup
import base64


def login_required_for_id(f):

  @wraps(f)
  def decorated_function(id, *args, **kwargs):
    if 'username' not in session or session['username'] != id:
      return redirect('/login')
    return f(id, *args, **kwargs)

  return decorated_function


app = Flask(__name__)
app.secret_key = 'secretestkey'


@app.route('/')
def home():
  return render_template('home.html')


@app.route('/signup', methods=['get', 'post'])
def signupform():
  if request.method == 'POST':
    user = request.form['username']
    pw = request.form['password']
    mail = request.form['email']
    result = signup(user, pw, mail)
    if result == 'success':
      return render_template('login.html')
    else:
      print('error')
  return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

  if request.method == 'POST':
    user = request.form['username']
    pw = request.form['password']
    data = login_user(user, pw)
    if data:
      session['username'] = data[0]
      session['index1'] = 0
      session['index2'] = 1
      return redirect('/user/{}'.format(user))

    else:
      print('error')

  return render_template('login.html')


@app.route("/user/<id>")
@login_required_for_id
def data_page(id):
  return render_template('loggedin.html', username=id)


@app.route('/loggedin', methods=['get'])
def loggedin():
  if 'username' in session:
    username = session['username']
    return render_template('loggedin.html', username=username)
  else:
    return redirect(url_for('login'))


@app.route('/uploaded', methods=['POST', 'GET'])
def uploading():
  imgs = request.files.getlist('imgs')
  print(imgs)
  if len(imgs) == 0:
    return "No picture Uploaded!", 400

  result = uploadImages(session['username'], imgs)
  if result == 'success':
    return redirect('/start')


@app.route('/start', methods=['get'])
def start():
  return render_template('uploaded.html')


@app.route('/compare', methods=['post', 'get'])
def compare():
  images = getimages('parth')
  length = len(images)
  session['length'] = length
  img1 = images[session['index1']]
  img2 = images[session['index2']]
  data1 = base64.b64encode(img1.image_data)
  data2 = base64.b64encode(img2.image_data)
  data1 = data1.decode('UTF-8')
  data2 = data2.decode('UTF-8')
  image1 = [data1, img1.img_name]
  image2 = [data2, img2.img_name]
  return render_template('main.html',
                         index1=session['index1'],
                         index2=session['index2'],
                         length=session['length'],
                         img1=image1,
                         img2=image2)


@app.route("/compare/<img_name>")
def inc_score(img_name):
  result = incScore(img_name, session['index1'], session['index2'],
                    session['length'])
  session['index1'] = result[0]
  session['index2'] = result[1]
  return redirect('/compare')
  return render_template('main.html')


@app.route("/logout")
def logout_page():
  session.pop('username', None)
  return redirect('/')


if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
