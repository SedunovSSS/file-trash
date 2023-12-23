from flask import Flask, render_template, redirect, request, make_response, abort, send_file
from flask_sqlalchemy import SQLAlchemy
import os, hashlib, shutil

app = Flask(__name__)

HOST = '0.0.0.0'
PORT = 8080
DEBUG = True

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['UPLOAD_FOLDER'] = 'static/user_trashes'
db = SQLAlchemy(app)

img = ['png', 'jpg', 'jpeg', 'gif', 'jfif', 'bmp', 'ico', 'webp', 'psd']
vid = ['mp4', 'mov', 'avi', 'wmv', 'avchd', 'webm', 'mkv', 'flv', 'f4v', 'swf', 'mpeg-2']
aud = ['mp3', 'm4a', 'ogg', 'wav', 'wma', 'mid', 'midi', 'aiff', 'au']
doc = ['doc', 'docx', 'rtf', 'dot', 'dotx']
ppt = ['ppt', 'pptx', 'pptm', 'xps', 'potx', 'potm', 'pot']
xls = ['xls', 'xlsx', 'csv']
htm = ['htm', 'html', 'xhtml']

accepted_2_open_types = ['text', 'html', 'image', 'audio', 'video', 'pdf']


def get_file_name_and_exp(name):
    for i in range(len(name)-1, -1, -1):
        if name[i] == '.':
            return name[:i], name[i+1:]
    return name, ''


def get_file_type_and_icon(exp):
    exp = exp.lower()
    if exp in img:
        return 'image', '/static/img/img.png'
    if exp in aud:
        return 'audio', '/static/img/audio.png'
    if exp in vid:
        return 'video', '/static/img/video.png'
    if exp in doc:
        return 'document', '/static/img/doc.png'
    if exp in 'ppt':
        return 'presentation', '/static/img/ppt.png'
    if exp in xls:
        return 'excel', '/static/img/xlsx.png'
    if exp in htm:
        return 'html', '/static/img/html.png'
    if exp == 'txt':
        return 'text', '/static/img/text.png'
    if exp == 'exe':
        return 'exe', '/static/img/exe-file.png'
    if exp == 'pdf':
        return 'pdf', '/static/img/pdf.png'
    return 'file', '/static/img/file.png'


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return '<Users %r>' % self.id
    
@app.errorhandler(404)
def _404(e):
    return render_template('404.html')

@app.errorhandler(500)
def _500(e):
    return render_template('500.html')

@app.route('/')
def index():
    name = request.cookies.get('user')
    if name is None:
        return redirect('/login')
    current = request.args.get('folder')
    if current is None:
        current = ''
    directory = f'static/user_trashes/{name}'
    if not os.path.exists(directory+'/'+current):
        return abort(404)
    files = []
    for i in os.listdir(directory+'/'+current):
        if os.path.isfile(directory+'/'+current+'/'+i):
            if '.' in i:
                fname, exp = get_file_name_and_exp(i)
                short_name = fname[:12] + '...' + fname[-3:] + '.' + exp  if len(fname) > 15 else fname + '.' + exp
                file_type, icon_apth = get_file_type_and_icon(exp)
            else:
                file_type, icon_apth = 'file', '/static/img/file.png'
                short_name = i[:12] + '...' if len(i) > 15 else i
        else:
            file_type, icon_apth = 'folder', '/static/img/folder.png'
            short_name = i[:12] + '...' if len(i) > 15 else i
        files.append({'name': short_name, 'fullname': i, 'isfile': os.path.isfile(directory+'/'+current+'/'+i), 'path': current+'/'+i, 'icon': icon_apth, \
                      'type': file_type, 'open': file_type in accepted_2_open_types})
    files = [files[i:i+4] for i in range(0, len(files), 4)]
    return render_template('index.html', files=files, current=current)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        password = hashlib.md5(password.encode("utf-8")).hexdigest()
        exists = db.session.query(Users.id).filter_by(login=login).first() is not None
        if exists:
            return redirect('/register')
        user = Users(login=login, password=password)
        try:
            db.session.add(user)
            db.session.commit()
            os.mkdir(f'static/user_trashes/{login}')
            resp = make_response(redirect("/"))
            resp.set_cookie('user', user.login)
            return resp
        except:
            return redirect("/register")
    else:
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        password = hashlib.md5(password.encode("utf-8")).hexdigest()
        exists = db.session.query(Users.id).filter_by(login=login).first() is not None
        if not exists:
            return redirect('/login')
        user = db.session.query(Users.login).filter_by(login=login, password=password).first()
        resp = make_response(redirect("/"))
        resp.set_cookie('user', user[0])
        return resp
    else:
        return render_template('login.html')
    
@app.route('/logout')
def logout():
    resp = make_response(redirect("/login"))
    resp.set_cookie('user', '', expires=0)
    return resp

@app.route('/add_folder', methods=['POST'])
def add_folder():
    name = request.cookies.get('user')
    if name is None:
        return redirect('/login')
    current = request.args.get('folder')
    if current is None:
        current = ''
    folder = request.form['foldername']
    fname = folder
    try:
        i = 1
        while folder in os.listdir(f'static/user_trashes/{name}/{current}'):
            folder = f'{fname} ({i})'
            i += 1
        if folder == '':
            return redirect(f'/?folder={current}')
        os.mkdir(f'static/user_trashes/{name}/{current}/{folder}')
    except:
        pass
    return redirect(f'/?folder={current}')

@app.route('/upload_file', methods=['POST'])
def upload_file():
    name = request.cookies.get('user')
    if name is None:
        return redirect('/login')
    current = request.args.get('folder')
    if current is None:
        current = ''
    file = request.files['file']
    try:
        filename = file.filename
        if '.' in filename:
            fname, exp = get_file_name_and_exp(filename)
            i = 1
            while filename in os.listdir(f'static/user_trashes/{name}/{current}'):
                filename = f'{fname} ({i}).{exp}'
                i += 1     
        else:
            fname = filename
            i = 1
            while filename in os.listdir(f'static/user_trashes/{name}/{current}'):
                filename = f'{fname} ({i})'
                i += 1
        file.save(f'static/user_trashes/{name}/{current}/{filename}')
    except:
        pass
    return redirect(f'/?folder={current}')

@app.route('/back')
def back():
    current = request.args.get('folder')
    if current is None:
        current = ''
    _dir = current.split('/')
    _dir = _dir[:-1]
    return redirect('/?folder='+'/'.join(_dir) if _dir != [''] else '/')

@app.route('/delete')
def delete():
    name = request.cookies.get('user')
    if name is None:
        return redirect('/login')
    current = request.args.get('object')
    object = f'static/user_trashes/{name}{current}'
    try:
        if os.path.isdir(object):
            shutil.rmtree(object)
        else:
            os.remove(object)
    except:
        pass
    _dir = current.split('/')
    _dir = _dir[:-1]
    return redirect('/?folder='+'/'.join(_dir) if _dir != [''] else '/')

@app.route('/download')
def download():
    name = request.cookies.get('user')
    if name is None:
        return redirect('/login')
    current = request.args.get('object')
    object = f'static/user_trashes/{name}{current}'
    try:
        return send_file(object, as_attachment=True)
    except:
        _dir = current.split('/')
        _dir = _dir[:-1]
        return redirect('/?folder='+'/'.join(_dir) if _dir != [''] else '/')

@app.route('/open')
def open_file():
    name = request.cookies.get('user')
    if name is None:
        return redirect('/login')
    current = request.args.get('object')
    object = f'static/user_trashes/{name}{current}'
    try:
        return send_file(object)
    except:
        _dir = current.split('/')
        _dir = _dir[:-1]
        return redirect('/?folder='+'/'.join(_dir) if _dir != [''] else '/')

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)
