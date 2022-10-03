from email.mime import image
from flask import Flask, session
from flask_login import LoginManager
from datetime import timedelta
# from flask_session import Session

login_manager = LoginManager()
login_manager.login_view = 'login'
webapp = Flask(__name__)
login_manager.init_app(webapp)
webapp.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=5)
### config for image uploading
UPLOAD_FOLDER = 'app/static/uploads/'
# AUTO_TEST_FOLDER = 'app/static/auto_test/'

webapp.secret_key = "secret key"
webapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# webapp.config['AUTO_TEST_FOLDER'] = AUTO_TEST_FOLDER
# maximum size 1 MB
webapp.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024



### mem-cache
webapp.config['MEM_CACHE_REQUEST_PREFIX'] = "http://localhost:5001/"


# SESSION_TYPE = 'filesystem'
# webapp.config.from_object(__name__)
# Session(webapp)


from app import main
from app import operations
#from app import memcache_operations
#from app import auto_test