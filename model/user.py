""" database dependencies to support sqliteDB examples """
from random import randrange
from datetime import date
import os, base64
import json

from flask_login import UserMixin

from __init__ import app, db
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from model.stocks import StockUser


''' Tutorial: https://www.sqlalchemy.org/library.html#tutorials, try to get into Python shell and follow along '''

""" Database Models """

class UserSection(db.Model):
    """ 
    UserSection Model

    A many-to-many relationship between the 'users' and 'sections' tables.

    Attributes:
        user_id (Column): An integer representing the user's unique identifier, a foreign key that references the 'users' table.
        section_id (Column): An integer representing the section's unique identifier, a foreign key that references the 'sections' table.
        year (Column): An integer representing the year the user enrolled with the section. Defaults to the current year.
    """
    __tablename__ = 'user_sections'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), primary_key=True)
    year = db.Column(db.Integer)

    # Relationship backrefs
    user = db.relationship("User", backref=db.backref("user_sections", cascade="all, delete-orphan"))
    section = db.relationship("Section", backref=db.backref("user_sections", cascade="all, delete-orphan"))

    def __init__(self, user, section):
        self.user = user
        self.section = section
        self.set_year_based_on_enrollment()

    def set_year_based_on_enrollment(self):
        current_month = date.today().month
        current_year = date.today().year
        # If current month is between August (8) and December (12), the enrollment year is next year.
        if 7 <= current_month <= 12:
            self.year = current_year + 1
        else:
            self.year = current_year

# Define a many-to-many relationship to 'users' table
class Section(db.Model):
    """
    Section Model
    
    The Section class represents a section within the application, such as a class, department or group.
    
    Attributes:
        id (db.Column): The primary key, an integer representing the unique identifier for the section.
        _name (db.Column): A string representing the name of the section. It is not unique and cannot be null.
        _abbreviation (db.Column): A unique string representing the abbreviation of the section's name. It cannot be null.
    """
    __tablename__ = 'sections'

    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(255), unique=False, nullable=False)
    _abbreviation = db.Column(db.String(255), unique=True, nullable=False)
    
    # Constructor
    def __init__(self, name, abbreviation):
        self._name = name 
        self._abbreviation = abbreviation
        
    @property
    def abbreviation(self):
        return self._abbreviation

    # String representation of the Classes object
    def __repr__(self):
        return f"Class(_id={self.id}, name={self._name}, abbreviation={self._abbreviation})"

    # CRUD create
    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    # CRUD read
    def read(self):
        return {
            "id": self.id,
            "name": self._name,
            "abbreviation": self._abbreviation
        }
        
    # CRUD delete: remove self
    # None
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None


# Define a User class that inherits from db.Model and UserMixin
class User(db.Model, UserMixin):
    """
    User Model

    This class represents the User model, which is used to manage actions in the 'users' table of the database. It is an
    implementation of Object Relational Mapping (ORM) using SQLAlchemy, allowing for easy interaction with the database
    using Python code. The User model includes various fields and methods to support user management, authentication,
    and profile management functionalities.

    Attributes:
        __tablename__ (str): Specifies the name of the table in the database.
        id (Column): The primary key, an integer representing the unique identifier for the user.
        _name (Column): A string representing the user's name. It is not unique and cannot be null.
        _uid (Column): A unique string identifier for the user, cannot be null.
        _password (Column): A string representing the hashed password of the user. It is not unique and cannot be null.
        _role (Column): A string representing the user's role within the application. Defaults to "User".
        _pfp (Column): A string representing the path to the user's profile picture. It can be null.
        kasm_server_needed (Column): A boolean indicating whether the user requires a Kasm server.
        sections (Relationship): A many-to-many relationship between users and sections, allowing users to be associated with multiple sections.
    """
    __tablename__ = 'users'  # table name is plural, class name is singular

    # Define the User schema with "vars" from object
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(255), unique=False, nullable=False)
    _uid = db.Column(db.String(255), unique=True, nullable=False)
    _password = db.Column(db.String(255), unique=False, nullable=False)
    _role = db.Column(db.String(20), default="User", nullable=False)
    _pfp = db.Column(db.String(255), unique=False, nullable=True)
    kasm_server_needed = db.Column(db.Boolean, default=False)
    
    # Relationship to manage the association between users and sections
    sections = db.relationship('Section', secondary=UserSection.__table__, lazy='subquery',
                               backref=db.backref('users', lazy=True))
    # One-One relationship with users and StockUsers
    stock_user = db.relationship("StockUser", backref=db.backref("users", cascade="all"), lazy=True,uselist=False)


    # Constructor of a User object, initializes the instance variables within object (self)
    def __init__(self, name, uid, password="123qwerty", kasm_server_needed=False, role="User", pfp=''):
        self._name = name
        self._uid = uid
        self.set_password(password)
        self.kasm_server_needed = kasm_server_needed
        self._role = role
        self._pfp = pfp

    # UserMixin/Flask-Login require a get_id method to return the id as a string
    def get_id(self):
        return str(self.id)

    # UserMixin/Flask-Login requires is_authenticated to be defined
    @property
    def is_authenticated(self):
        return True

    # UserMixin/Flask-Login requires is_active to be defined
    @property
    def is_active(self):
        return True

    # UserMixin/Flask-Login requires is_anonymous to be defined
    @property
    def is_anonymous(self):
        return False

    # a name getter method, extracts name from object
    @property
    def name(self):
        return self._name

    # a setter function, allows name to be updated after initial object creation
    @name.setter
    def name(self, name):
        self._name = name

    # a getter method, extracts email from object
    @property
    def uid(self):
        return self._uid

    # a setter function, allows name to be updated after initial object creation
    @uid.setter
    def uid(self, uid):
        self._uid = uid

    # check if uid parameter matches user id in object, return boolean
    def is_uid(self, uid):
        return self._uid == uid

    @property
    def password(self):
        return self._password[0:10] + "..."  # because of security only show 1st characters

    # update password, this is conventional setter
    def set_password(self, password):
        """Create a hashed password."""
        self._password = generate_password_hash(password, "pbkdf2:sha256", salt_length=10)

    # check password parameter versus stored/encrypted password
    def is_password(self, password):
        """Check against hashed password."""
        result = check_password_hash(self._password, password)
        return result

    # output content using str(object) in human readable form, uses getter
    # output content using json dumps, this is ready for API response
    def __str__(self):
        return json.dumps(self.read())

    @property
    def role(self):
        return self._role

    @role.setter
    def role(self, role):
        self._role = role

    def is_admin(self):
        return self._role == "Admin"
    
    # getter method for profile picture
    @property
    def pfp(self):
        return self._pfp

    # setter function for profile picture
    @pfp.setter
    def pfp(self, pfp):
        self._pfp = pfp

    # CRUD create/add a new record to the table
    # returns self or None on error
    def create(self):
        try:
            db.session.add(self)  # add prepares to persist person object to Users table
            db.session.commit()  # SqlAlchemy "unit of work pattern" requires a manual commit
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    # CRUD read converts self to dictionary
    # returns dictionary
    def read(self):
        return {
            "id": self.id,
            "name": self.name,
            "uid": self.uid,
            "role": self._role,
            "pfp": self._pfp,
            "kasm_server_needed": self.kasm_server_needed,
            "sections": [section.read() for section in self.sections] if self.sections else None
        }
        
    # CRUD update: updates user name, password, phone
    # returns self
    def update(self, name="", uid="", password="", pfp=None, kasm_server_needed=None):
        """only updates values with length"""
        if len(name) > 0:
            self.name = name
        if len(uid) > 0:
            self.uid = uid
        if len(password) > 0:
            self.set_password(password)
        if pfp is not None:  # here we explicitly check for None to allow setting pfp to None
            self.pfp = pfp
        if kasm_server_needed is not None:
            self.kasm_server_needed = kasm_server_needed
        db.session.commit()
        return self
    
    # CRUD delete: remove self
    # None
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None
    
    
    def save_pfp(self, image_data, filename):
        """For saving profile picture."""
        try:
            user_dir = os.path.join(app.config['UPLOAD_FOLDER'], self.uid)
            if not os.path.exists(user_dir):
                os.makedirs(user_dir)
            file_path = os.path.join(user_dir, filename)
            with open(file_path, 'wb') as img_file:
                img_file.write(image_data)
            self.update(pfp=filename)
        except Exception as e:
            raise e
        
    def delete_pfp(self):
        """Deletes profile picture from user record."""
        self.pfp = None
        db.session.commit()
        
    def read_sections(self):
        return { "sections": [section.read() for section in self.sections] if self.sections else None }
    
    def add_section(self, section):
        # Query for the section using the provided abbreviation
        found = any(s.id == section.id for s in self.sections)
        
        # Check if the section was found
        if not found:
            # Add the section to the user's sections
            user_section = UserSection(user=self, section=section)
            db.session.add(user_section)
            
            # Commit the changes to the database
            db.session.commit()
        else:
            # Handle the case where the section exists
            print("Section with abbreviation '{}' exists.".format(section._abbreviation))
        return self
    
    def add_sections(self, sections):
        for section in sections:
            section_obj = Section.query.filter_by(_abbreviation=section).first()
            if not section_obj:
                return None
            self.add_section(section_obj)
        return self
    
    def remove_sections(self, section_abbreviations):
        try:
            for abbreviation in section_abbreviations:
                section = next((section for section in self.sections if section.abbreviation == abbreviation), None)
                if section:
                    self.sections.remove(section)
                else:
                    raise ValueError(f"Section with abbreviation '{abbreviation}' not found.")
            db.session.commit()
            return True
        except ValueError as e:
            db.session.rollback()
            print(e)  # Log the specific abbreviation error
            return False
        except Exception as e:
            db.session.rollback()
            print(f"Unexpected error removing sections: {e}")
            return False
    # creates a new log to StockUser table. Refers User table
    # purpose: realtes to actual user in user table but doen't interfer with other things on user table
    def add_stockuser(self, uid):
        user = User.query.filter_by(_uid=uid).first()
        if user:
            found = user.stock_user is not None
            if not found:
                stock_user = StockUser(user_id=user.uid, stockmoney=100000, accountdate=date.today())
                db.session.add(stock_user)
                db.session.commit()
            else:
                print(f"StockUser for user {uid} already exists.")
    """Database Creation and Testing """

# Builds working data set for testing
def initUsers():
    with app.app_context():
        """Create database and tables"""
        db.create_all()
        """Tester data for table"""
        
        u1 = User(name='Thomas Edison', uid='toby', password='123toby', pfp='toby.png', kasm_server_needed=True, role="Admin")
        u2 = User(name='Nicholas Tesla', uid='niko', password='123niko', pfp='niko.png', kasm_server_needed=False)
        u3 = User(name='Alexander Graham Bell', uid='lex', password='123lex', pfp='lex.png', kasm_server_needed=True)
        u4 = User(name='Grace Hopper', uid='hop', password='123hop', pfp='hop.png', kasm_server_needed=False)
        u5 = User(name='Fred Flintstone', uid='fred', pfp='fred.png', kasm_server_needed=True)
        users = [u1, u2, u3, u4, u5]
        
        for user in users:
            try:
                user.create()
            except IntegrityError:
                '''fails with bad or duplicate data'''
                db.session.remove()
                print(f"Records exist, duplicate email, or error: {user.uid}")

        s1 = Section(name='Computer Science A', abbreviation='CSA')
        s2 = Section(name='Computer Science Principles', abbreviation='CSP')
        s3 = Section(name='Engineering Robotics', abbreviation='Robotics')
        s4 = Section(name='Computer Science and Software Engineering', abbreviation='CSSE')
        sections = [s1, s2, s3, s4]
        
        for section in sections:
            try:
                section.create()    
            except IntegrityError:
                '''fails with bad or duplicate data'''
                db.session.remove()
                print(f"Records exist, duplicate email, or error: {section.name}")
            
        u1.add_section(s1)
        u1.add_section(s2)
        u2.add_section(s2)
        u2.add_section(s3)
        u3.add_section(s3)
        u4.add_section(s4)
        u4.add_section(s4)
        