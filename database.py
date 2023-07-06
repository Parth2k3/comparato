from sqlalchemy import create_engine, text
import os

db_connection_string = os.environ['DB_CONNECTION_STRING']

engine = create_engine(db_connection_string,
                       connect_args={"ssl": {
                         "ssl_ca": "/etc/ssl/cert.pem"
                       }})


def signup(user, pw, mail):
  with engine.connect() as conn:
    conn.execute(text('INSERT into users(`username`,`pass`,`mail`) values (:user, :pw, :mail)'), {
      "user": user,
      "pw": pw,
      "mail": mail
    })
    return 'success'

def login_user(username, password):
  with engine.connect() as conn:
    result = conn.execute(
      text("SELECT * FROM users WHERE username = :user AND pass = :passw"), {
        "user": username,
        "passw": password
      })
    rows = result.all()
    print(rows)
    if len(rows) == 0:
      return None
    else:
      return list(rows[0])


def uploadImages(username, imgs):
  with engine.connect() as conn:
    for img in imgs:
      imgdata = img.read()
      name = img.filename
      score = 0

      conn.execute(
        text(
          "INSERT INTO images (`user`, `image_data`, `score`, `img_name`) values(:user, :thepic, :score, :name)"
        ), {
          "user": username,
          "thepic": imgdata,
          "score": score,
          "name": name
        })
    return 'success'


def getimages(username):
  with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM images where user = :user"),
                          {"user": username})
    rows = result.all()
    if len(rows) == 0:
      return None
    else:
      return list(rows)


def incScore(img_name, i1, i2, length):

  with engine.connect() as conn:
    conn.execute(
      text("UPDATE images SET score = score + 1 WHERE img_name = :img_name"),
      {"img_name": img_name})

  if i2 == length - 1:
    i1 = i1 + 1
    i2 = i1 + 1
  if i1 == length - 1:
    return 'end'
  else:
    i2 = i2 + 1
  return [i1, i2]
