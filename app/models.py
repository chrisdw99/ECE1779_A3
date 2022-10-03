from flask_login import UserMixin
from app import login_manager
from werkzeug.security import check_password_hash
from app import dynamodb_operations as dy_ope
class User(UserMixin):
    def is_authenticated(self):
        #a property that is True if the user has valid credentials or False otherwise.
        return self.authenticated
    
    def is_active(self):
        # a property that is True if the user's account is active or False otherwise.
        return self.active
    def is_anonymous(self):
        return self.anonymous

    def get_id(self):
        #a method that returns a unique identifier for the user as a string
        return self.id
    def is_admin(self):
        return self.admin
    # def set_file_status(self,has_file):
    #     self.file_status=has_file
    # def does_have_file(self):
    #     return self.has_file 
    def find_user_by_id(id):
        #print("called find function.")
        result = dy_ope.find_user_by_id(id)
        if result == {} or result == None:
            return None
        else:
            if "admin_no" in result:
                return User.set_user(result,True)
            else:
                return User.set_user(result,False)
    def check_password_only(id,password):
        result = dy_ope.find_user_by_id(id)
        if result == {} or result == None:
            return None
        else:
            if "passwd_hash" in result:
                if check_password_hash(result["passwd_hash"],password):
                    return True
                else:
                    return False
            else:
                return None
    def update_password(id,password):
        info = {"id":id,"password":password}
        result = dy_ope.update_password(info)
        return result
            
    def check_login(email,password):
        result = dy_ope.find_user_by_email(email)
        if result == None:
            return None
        elif result == {}:
            return "Not exists"
        else:
            if check_password_hash(result["passwd_hash"],password):
                if "admin_no" in result:
                    return User.set_user(result,True)
                else:
                    return User.set_user(result,False)
            else:
                return "Wrong Passwd"
    def set_user(info:dict, admin:bool):
        user = User()
        user.id = info["userid"]
        user.email = info["email"]
        user.authenticated = True
        user.active = True
        user.anonymous = False
        user.admin = admin
        #user.has_file = False
        #record_user = user
        return user
    def __repr__(self):
        return '<User {} with email {}>'.format(self.id,self.email)
    # id = ""
    # email = ""
    # authenticated = False
    # anonymous = True
    # active = False
    # admin = False
    # setted = False
init_info = {"userid":"","email":""}
record_user = User()
record_user.id = ""
@login_manager.user_loader
def load_user(id):
    return User.find_user_by_id(id)
    