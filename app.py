import os

from flask import Flask
# from pymongo import MongoClient
from pymongo.errors import PyMongoError
from flask import request  # jsonify    ,abort

import mysql.connector

import logging
import time

import random
import string

# from config import MONGO_DB_CONNECTION_STRING

# TODO: Change this to mysql
# client = MongoClient(MONGO_DB_CONNECTION_STRING)
# db = client['grade-logging-api']
# GRADE = db['grade']
# TOKEN = db['token']
# TEAM = db['team']

# create a connection to the database
# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Log to console
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Also log to a file
file_handler = logging.FileHandler("cpy-errors.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

if os.path.isfile('server_data.txt'):
    with open('server_data.txt', 'r') as f:
        lines = f.readlines()
        user = lines[0].strip()
        password = lines[1].strip()
        host = lines[2].strip()
        database = lines[3].strip()
else:
    exit(code="Config file error")

config = {
    'user': user,
    'password': password,
    'host': host,
    'database': database,
    'raise_on_warnings': True
}


def connect_to_mysql(config, attempts=3, delay=2):
    attempt = 1
    # Implement a reconnection routine
    while attempt < attempts + 1:
        try:
            return mysql.connector.connect(**config)
        except (mysql.connector.Error, IOError) as err:
            if attempts is attempt:
                # Attempts to reconnect failed; returning None
                logger.info("Failed to connect, exiting without a connection: %s", err)
                return None
            logger.info(
                "Connection failed: %s. Retrying (%d/%d)...",
                err,
                attempt,
                attempts - 1,
            )
            # progressive reconnect delay
            time.sleep(delay ** attempt)
            attempt += 1
    return None


app = Flask(__name__)


def api_key_middleware():
    db = connect_to_mysql(config)
    if db is None:
        return {
            "status_code": 401,
            "message": "Error Connecting to Database"
        }, 401

    if request.endpoint in ['signUp']: return
    if request.endpoint in ['signIn']: return
    if request.endpoint in ['existsByName']: return
    authorization_header = request.headers.get("Authorization")
    # check if get method.
    if request.method == 'GET':
        utorid = request.args.get('utorid') if 'utorid' in request.args else None
    else:
        utorid = request.json['utorid'] if 'utorid' in request.json else None
    if not authorization_header:
        return {
            "status_code": 401,
            "message": "Authorization header is required"
        }, 401

    if utorid is None:
        return {
            "status_code": 400,
            "message": "utorid is required"
        }, 400

    # check if the token is valid.
    # the_doc = TOKEN.find_one({
    #     "utorid": utorid
    # })
    the_doc = {'123455': 123543, 'token': "EXAMPLE_TOKEN"}

    if not the_doc:
        return {
            "status_code": 401,
            "message": "The UTORid is not associated with a token. Please sign up first."
        }, 401

    if authorization_header != the_doc['token']:
        return {
            "status_code": 401,
            "message": "Invalid token"
        }, 401


@app.route('/signUp', methods=['GET'])
def signUp():
    """Sign a user up"""

    # get parameters from request
    input_username = request.args.get('username') if 'username' in request.args else None
    password = request.args.get('password') if 'password' in request.args else None

    if input_username is None or password is None:
        return {
            "status_code": 401,
            "message": "NO PASSWORD or USERNAME GIVEN"
        }, 401

    # connect to database
    db = connect_to_mysql(config)
    if db is None:
        return {
            "status_code": 408,
            "message": "Error Connecting to Database. Request has timedout. Please contact Support"
        }, 408

    cursor = db.cursor()

    # first, see if this utorid is associated with a token.
    query = 'SELECT username FROM users WHERE username =%s'
    cursor.execute(query, [input_username])
    result = cursor.fetchall()

    if result:
        db.close()
        return {
            "status_code": 400,
            "message": "USERNAME ALREADY EXISTS"
        }, 400

    # generate deployment api token.
    def generate_token(length=32):
        """Generate a random user token"""
        # Define the characters that can be used in the token
        characters = string.ascii_letters + string.digits

        # Generate a random token using the specified length
        token = ''.join(random.choice(characters) for _ in range(length))

        return token

    token = generate_token()

    # save user to DB.
    insert_user_query = "INSERT INTO users (username, password, token) VALUES (%s, %s, %s)"
    user = (input_username, password, token)
    cursor.execute(insert_user_query, user)

    db.commit()
    db.close()

    # return with token
    return {
        "status_code": 200,
        "message": "Token generated successfully",
        "token": token
    }, 200


@app.route('/signIn', methods=['GET'])
def signIn():
    """Sign a user in"""

    # get parameters from request
    input_username = request.args.get('username') if 'username' in request.args else None
    password = request.args.get('password') if 'password' in request.args else None

    if input_username is None or password is None:
        return {
            "status_code": 401,
            "message": "NO PASSWORD or USERNAME GIVEN"
        }, 401

    # connect to database
    db = connect_to_mysql(config)
    if db is None:
        return {
            "status_code": 408,
            "message": "Error Connecting to Database. Request has timedout. Please contact Support"
        }, 408

    cursor = db.cursor()

    # first, see if this utorid is associated with a token.
    query = 'SELECT token FROM users WHERE username =%s AND password =%s'
    cursor.execute(query, (input_username, password))
    token = cursor.fetchall()

    db.close()

    if not token:
        return {
            "status_code": 400,
            "message": "PASSWORD OR USERNAME INCORRECT"
        }, 400

    # return with token
    return {
        "status_code": 200,
        "message": "LOGIN SUCESSFUL",
        "token": token[0][0]
    }, 200


@app.route('/existsByName', methods=['GET'])
def existsByName():
    """Sign a user in"""

    # get parameters from request
    input_username = request.args.get('username') if 'username' in request.args else None

    # connect to database
    db = connect_to_mysql(config)
    if db is None:
        return {
            "status_code": 408,
            "message": "Error Connecting to Database. Request has timedout. Please contact Support"
        }, 408

    cursor = db.cursor()

    # first, see if this utorid is associated with a token.
    query = 'SELECT token FROM users WHERE username =%s'
    cursor.execute(query, [input_username])
    token = cursor.fetchall()

    db.close()

    if not token:
        return {
            "status_code": 200,
            "message": "USER DOES NOT EXISTS"
        }, 200

    # return with token
    return {
        "status_code": 200,
        "message": "USER EXISTS"
    }, 200


@app.before_request
def before_request():
    response = api_key_middleware()
    if response is not None:
        return response


# An API that creates a grade document.
# The request body should be a JSON object with the following fields:
# utorid: the utorid of the student
# course: the course code
# grade: the grade of the student
# The response body should be a JSON object with the following fields:
# status: a code
# message: "Grade created successfully" if the grade document is created successfully, "Error creating grade" otherwise
# id: the id of the grade document created
@app.route('/grade', methods=['POST'])
def create_grade():
    try:
        utorid = request.json['utorid'] if 'utorid' in request.json else None
        course = request.json['course'] if 'course' in request.json else None
        grade = request.json['grade'] if 'grade' in request.json else None

        if not utorid or not course or not grade:
            return {
                "status_code": 400,
                "message": "utorid, course, and grade are required"
            }, 400

        # check if the grade is valid.
        if not isinstance(grade, int) or grade < 0 or grade > 100:
            return {
                "status_code": 400,
                "message": "grade must be an integer between 0 and 100"
            }, 400

        # check if the grade document already exists

        # TODO: CHANGE THIS TO MYSQL
        # the_doc = GRADE.find_one({
        #     "utorid": utorid,
        #     "course": course
        # })

        the_doc = True
        if the_doc:
            return {
                "status_code": 400,
                "message": "Grade already exists (THIS IS NOT IMPLEMENTED)"
            }, 400
        # TODO CHANGE THIS TO MYSQL
        # grade_id = GRADE.insert_one({
        #     "utorid": utorid,
        #     "course": course,
        #     "grade": grade
        # }).inserted_id
        # return {
        #     "status_code": 200,
        #     "message": "Grade created successfully",
        #     "id": str(grade_id)
        # }, 200
    except PyMongoError as e:
        print(e)
        return {
            "status_code": 500,
            "message": "Error creating grade"
        }, 500


# An API that returns a grade document, it's a get request with the following path: grade/course/utorid
# The response body should be a JSON object with the following fields:
# status: a code
# message: "Grade retrieved successfully" if the grade document is retrieved successfully, "Error retrieving grade" otherwise
# grade: the grade of the student
@app.route('/grade', methods=['GET'])
def get_grade():
    try:
        utorid = request.args.get('utorid') if 'utorid' in request.args else None
        course = request.args.get('course') if 'course' in request.args else None

        # TODO: CHANGE THIS TO MYSQL
        # the_doc = GRADE.find_one({
        #     "utorid": utorid,
        #     "course": course
        # })

        the_doc = True
        if not the_doc:
            return {
                "status_code": 404,
                "message": "Grade not found (NOT IMPLEMENTED YET)"
            }, 404

        the_doc = {"utorid": "BILLYBOB(TEST)", "grade": 100}
        return {
            "status_code": 200,
            "message": "Grade retrieved successfully",
            "utorid": the_doc['utorid'],
            "grade": {
                "_id": {
                    "$oid": "64b85b05e66b09ca82769e67"
                },
                "course": "CSC207",
                "grade": 85,
                "utorid": "t1chenpa"
            }
        }, 200
        # return {
        #     "grade": {
        #         "_id": {
        #             "$oid": "64b85b05e66b09ca82769e67"
        #         },
        #         "course": "CSC207",
        #         "grade": 85,
        #         "utorid": "t1chenpa"
        #     },
        #     "message": "Grade retrieved successfully",
        #     "status_code": 200,
        #     "utorid": "t1chenpa"
        # }
    except PyMongoError as e:
        print(e)
        return {
            "status_code": 500,
            "message": "Error retrieving grade"
        }, 500
    except Exception as e:
        print("error")
        print(e)
        return {
            "status_code": 500,
            "message": "Error retrieving grade"
        }, 500


# An API that updates a grade document.
# The request body should be a JSON object with the following fields:
# utorid: the utorid of the student
# course: the course code
# grade: the grade of the student
# The response body should be a JSON object with the following fields:
# status: a code
# message: "Grade updated successfully" if the grade document is updated successfully, "Error updating grade" otherwise
@app.route('/grade', methods=['PUT'])
def update_grade():
    try:
        utorid = request.json['utorid'] if 'utorid' in request.json else None
        course = request.json['course'] if 'course' in request.json else None
        grade = request.json['grade'] if 'grade' in request.json else None

        if not utorid or not course or not grade:
            return {
                "status_code": 400,
                "message": "utorid, course, and grade are required"
            }

        # check if the grade is valid.
        if not isinstance(grade, int) or grade < 0 or grade > 100:
            return {
                "status_code": 400,
                "message": "grade must be an integer between 0 and 100"
            }

        # check if the grade document already exists

        # TODO: CHANGE THIS TO MYSQL
        # the_doc = GRADE.find_one({
        #     "utorid": utorid,
        #     "course": course
        # })

        the_doc = False
        if not the_doc:
            return {
                "status_code": 404,
                "message": "The grade does not exist, please create it first using POST /grade"
            }

        # TODO: CHANGE THIS TO MYSQL
        # GRADE.update_one({
        #     "_id": the_doc['_id']
        # }, {
        #     "$set": {
        #         "grade": grade
        #     }
        # })
        return {
            "status_code": 200,
            "message": "Grade updated successfully"
        }
    except PyMongoError as e:
        print(e)
        return {
            "status_code": 500,
            "message": "Error updating grade"
        }


# An API that deletes a grade document.
# The request body should be a JSON object with the following fields:
# utorid: the utorid of the student
# course: the course code
# The response body should be a JSON object with the following fields:
# status: a code
# message: "Grade deleted successfully" if the grade document is deleted successfully, "Error deleting grade" otherwise
@app.route('/grade', methods=['DELETE'])
def delete_grade():
    try:
        utorid = request.json['utorid'] if 'utorid' in request.json else None
        course = request.json['course'] if 'course' in request.json else None

        if not utorid or not course:
            return {
                "status_code": 400,
                "message": "utorid, course are required"
            }

        # check if the grade document already exists

        # TODO: CHANGE THIS TO MYSQL
        # the_doc = GRADE.find_one({
        #     "utorid": utorid,
        #     "course": course
        # })

        the_doc = False
        if not the_doc:
            return {
                "status_code": 404,
                "message": "The grade does not exist, there's no need to delete it."
            }

        # TODO: CHANGE THIS TO MYSQL
        # GRADE.delete_one({
        #     "_id": the_doc['_id']
        # })
        return {
            "status_code": 200,
            "message": "Grade deleted successfully"
        }
    except PyMongoError as e:
        print(e)
        return {
            "status_code": 500,
            "message": "Error updating grade"
        }


# form a team.
@app.route('/team', methods=['POST'])
def form_team():
    name = request.json['name'] if 'name' in request.json else None
    utorid = request.json['utorid'] if 'utorid' in request.json else None

    if not name or not utorid:
        return {
            "status_code": 400,
            "message": "utorid and name are required"
        }, 400

    # TODO: CHANGE THIS TO MYSQL
    # check if the team already exists.
    # the_doc = TEAM.find_one({
    #     "name": name
    # })

    the_doc = True
    if the_doc:
        return {
            "status_code": 400,
            "message": "Team already exists"
        }, 400

    # check if the utorid is already in a team.
    # the_doc = TEAM.find_one({
    #     "members": {"$in": [utorid]}
    # })

    the_doc = True
    if the_doc:
        return {
            "status_code": 400,
            "message": "You are already in a team"
        }, 400

    # TODO: CHANGE THIS TO MYSQL
    # create a team.
    # TEAM.insert_one({
    #     "name": name,
    #     "members": [utorid]
    # })

    return {
        "status_code": 200,
        "message": f'Team {name} created successfully'
    }, 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=20112, debug=True, threaded=True)
