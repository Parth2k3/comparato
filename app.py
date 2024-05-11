from flask import Flask, render_template, request, session, redirect, url_for
from functools import wraps
from database import login_user, uploadImages, getimages, incScore, signup, getResult, modifyName, deleteImage, getImageByName, getVoters
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


@app.route('/loggedin/<id>', methods=['get'])
@login_required_for_id
def loggedin(id):
  if 'username' in session:
    username = session['username']
    return render_template('loggedin.html', username=username)
  else:
    return redirect(url_for('login'))


@app.route('/uploaded/<id>', methods=['POST', 'GET'])
@login_required_for_id
def uploading(id):
  imgs = request.files.getlist('imgs')
  if len(imgs) == 0:
    return "No picture Uploaded!", 400

  result = uploadImages(session['username'], imgs)
  if result == 'success':
    return redirect('/start/{}'.format(id))


@app.route('/start/<id>', methods=['get'])
@login_required_for_id
def start(id):
  return render_template('uploaded.html', username=id)


@app.route('/compare/<id>', methods=['post', 'get'])
@login_required_for_id
def compare(id):
  images = getimages(id)
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
                         user=id,
                         index1=session['index1'],
                         index2=session['index2'],
                         length=session['length'],
                         img1=image1,
                         img2=image2)


@app.route("/comparing/<user>/<img_name>")
def inc_score(user, img_name):
  result = incScore(user, img_name, session['index1'], session['index2'],
                    session['length'], session['username2'])
  username = session['username']
  if result == 'end':
    session['index1'] = 0
    session['index2'] = 1
    return redirect('/results/{}'.format(username))
  session['index1'] = result[0]
  session['index2'] = result[1]
  return redirect('/compare/{}'.format(username))
  return render_template('main.html')


@app.route("/comparingfor/<user>/<img_name>")
def inc_scorefor(user, img_name):
  result = incScore(user, img_name, session['index1'], session['index2'],
                    session['length'], session['username2'])

  if result == 'end':
    session['index1'] = 0
    session['index2'] = 1
    return redirect('/results/{}'.format(user))
  session['index1'] = result[0]
  session['index2'] = result[1]
  return redirect('/compareForStart/{}'.format(user))
  return render_template('main.html')


@app.route("/results/<id>")
@login_required_for_id
def results(id):
  result = getResult(id)
  list = []
  for img in result:
    data = base64.b64encode(img.image_data)
    data = data.decode('UTF-8')
    score = img.score
    name = img.img_name
    element = [data, score, name]
    list.append(element)
    
  return render_template('result.html', user=id, sortedImages=list)


@app.route("/comparefor/<user1>", methods=['get', 'post'])
def comparefor(user1):
  if request.method == 'POST':
    user2 = request.form['username']
    session['username2'] = user2
    session['index1'] = 0
    session['index2'] = 1
    return redirect('/compareForStart/{}'.format(user1))
  return render_template('compareFor.html', user=user1)


@app.route('/compareForStart/<user>')
def startcomp(user):

  if 'username2' not in session:
    redirect('/comparefor/{}'.format(user))

  images = getimages(user)
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
  return render_template('compareForStart.html',
                         user = user,
                         index1=session['index1'],
                         index2=session['index2'],
                         length=session['length'],
                         img1=image1,
                         img2=image2)


@app.route("/modify/<id>")
@login_required_for_id
def modify(id):
  images = getimages(id)
  list = []
  for img in images:
    data = base64.b64encode(img.image_data)
    data = data.decode('UTF-8')
    score = img.score
    name = img.img_name
    element = [data, score, name]
    list.append(element)

  return render_template('modify.html', user=id, Imageslist=list)


@app.route("/modifyname/<id>/<img_name>", methods=['get', 'post'])
@login_required_for_id
def modifynameimage(id, img_name):
  if request.method == 'POST':
    newname = request.form['newname']

    modifyName(id, img_name, newname)
    return redirect('/modify/{}'.format(id))
  image = getImageByName(id, img_name)
  img = image[0]
  data = base64.b64encode(img.image_data)
  data = data.decode('UTF-8')
  score = img.score
  name = img.img_name
  element = [data, score, name]

  return render_template('modifyname.html', user=id, image=element)


@app.route("/modifyimage/<id>/<img_name>")
@login_required_for_id
def modifyimage(id, img_name):
  deleteImage(id, img_name)
  return redirect('/modify/{}'.format(id))


@app.route("/logout")
def logout_page():
  session.pop('username', None)
  return redirect('/modify/{}'.format(id))


if __name__ == '__main__':

  app.run(host='0.0.0.0', debug=True)
