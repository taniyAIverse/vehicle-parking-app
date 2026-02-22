from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

db= SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app= Flask(__name__)

    app.config['SECRET_KEY'] = "tan@123"
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.signin'
   

    from .models import User, Admin
    
    @login_manager.user_loader
    def load_user(user_id):
        role, id = user_id.split("-", 1)
        if role == "user":
            return User.query.get(int(id))
        elif role == "admin":
            return Admin.query.get(int(id))
        return None


    from .controllers.main import main as main_blueprint
    from .controllers.admin import admin as admin_blueprint
    from .controllers.user import user as user_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(user_blueprint)



    with app.app_context():
        db.create_all()
        
        admin=Admin.query.first()
        if not admin:
            username="admin@123"
            password=generate_password_hash("admin123")
            name= "Admin"
            new_admin=Admin(username=username, password=password, name=name)
            db.session.add(new_admin)
            db.session.commit()    
    
    return app

