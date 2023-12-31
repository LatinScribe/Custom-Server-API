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
        id = request.args.get('id') if 'id' in request.args else None
    else:
        id = request.json['id'] if 'id' in request.json else None
    if not authorization_header:
        return {
            "status_code": 401,
            "message": "Authorization header is required"
        }, 401

    if id is None:
        return {
            "status_code": 400,
            "message": "id is required"
        }, 400

    # check if the token is valid.
    # So if it is associated with an account
    # the_doc = TOKEN.find_one({
    #     "utorid": utorid
    # })
    # the_doc = {'123455': 123543, 'token': "EXAMPLE_TOKEN"}

    # connect to database
    db = connect_to_mysql(config)
    if db is None:
        return {
            "status_code": 408,
            "message": "Error Connecting to Database. Request has timedout. Please contact Support"
        }, 408

    cursor = db.cursor()

    query = 'SELECT token FROM users WHERE id =%s'
    cursor.execute(query, [str(id)])
    token = cursor.fetchall()

    # query2 = 'SELECT token FROM profiles WHERE id =%s'
    # cursor.execute(query2, [str(id)])
    # token2 = cursor.fetchall()

    db.close()

    if not token:
        return {
            "status_code": 400,
            "message": "The id is not associated with a token. Please sign up first."
        }, 400

    # if not token2:
    #     return {
    #         "status_code": 401,
    #         "message": "The id is not associated with a profile. Please create an account first."
    #     }, 401

    if authorization_header != token[0][0]:
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
            "status_code": 400,
            "message": "NO PASSWORD or USERNAME GIVEN"
        }, 400

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

    query = 'SELECT id FROM users WHERE username =%s'
    cursor.execute(query, [input_username])
    id = cursor.fetchall()

    db.close()

    # return with token
    return {
        "status_code": 200,
        "message": "Token generated successfully",
        "id": id[0][0],
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
            "status_code": 400,
            "message": "NO PASSWORD or USERNAME GIVEN"
        }, 400

    # connect to database
    db = connect_to_mysql(config)
    if db is None:
        return {
            "status_code": 408,
            "message": "Error Connecting to Database. Request has timedout. Please contact Support"
        }, 408

    cursor = db.cursor()

    # first, see if this utorid is associated with a token.
    query = 'SELECT id,token FROM users WHERE username =%s AND password =%s'
    cursor.execute(query, (input_username, password))
    result = cursor.fetchall()

    db.close()

    if not result:
        return {
            "status_code": 400,
            "message": "PASSWORD OR USERNAME INCORRECT"
        }, 400

    # return with token
    return {
        "status_code": 200,
        "message": "LOGIN SUCESSFUL",
        "id": result[0][0],
        "token": result[0][1]
    }, 200


@app.route('/existsByName', methods=['GET'])
def existsByName():
    """Sign a user in"""

    # get parameters from request
    input_username = request.args.get('username') if 'username' in request.args else None

    if input_username is None:
        return {
            "status_code": 400,
            "message": "NO USERNAME GIVEN"
        }, 400

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
            "message": "USER DOES NOT EXIST"
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

@app.route('/saveProfile', methods=['POST'])
def saveProfile():
    try:
        id = request.json['id'] if 'id' in request.json else None
        token = request.headers.get("Authorization")
        finAidReq = request.json['finAidReq'] if 'finAidReq' in request.json else None
        prefProg = request.json['prefProg'] if 'prefProg' in request.json else None
        avgSalary = request.json['avgSalary'] if 'avgSalary' in request.json else None
        uniRankingRangeStart = request.json['uniRankingRangeStart'] if 'uniRankingRangeStart' in request.json else None
        uniRankingRangeEnd = request.json['uniRankingRangeEnd'] if 'uniRankingRangeEnd' in request.json else None
        locationPref = request.json['locationPref'] if 'locationPref' in request.json else None

        if not id or not token or not finAidReq or not prefProg or not avgSalary or not uniRankingRangeStart or not uniRankingRangeEnd or not locationPref:
            return {
                "status_code": 400,
                "message": "id, token, finAidReq, prefProg, avgSalary, uniRankingRangeStart, uniRankingRangeEnd, locationPref are required"
            }, 400

        db = connect_to_mysql(config)
        if db is None:
            return {
                "status_code": 408,
                "message": "Error Connecting to Database. Request has timedout. Please contact Support"
            }, 408

        cursor = db.cursor()
        # check if the user is already exists in the profile
        query2 = 'SELECT token FROM profiles WHERE id =%s'
        cursor.execute(query2, [str(id)])
        token2 = cursor.fetchall()

        if token2:
            return {
            "status_code": 400,
            "message": "This user already has a profile in the system. If you want to moddify the profile, please use updateProfile instead"
        }, 400

        # save user to DB.
        insert_user_query = "INSERT INTO profiles (id, token, finAidReq, prefProg, avgSalary, uniRankingRangeStart, uniRankingRangeEnd, locationPref) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        profile = (id, token, finAidReq, prefProg, avgSalary, uniRankingRangeStart, uniRankingRangeEnd, locationPref)
        cursor.execute(insert_user_query, profile)

        db.commit()

        db.close()

    except Exception as e:
        print(e)
        return {
            "status_code": 500,
            "message": "Error saving profile"
        }, 500

    return {
        "status_code": 200,
        "message": "Profile Saved Successfully"
    }, 200



@app.route('/updateProfile', methods=['PUT'])
def updateProfile():
    try:
        id = request.json['id'] if 'id' in request.json else None
        token = request.headers.get("Authorization")
        finAidReq = request.json['finAidReq'] if 'finAidReq' in request.json else None
        prefProg = request.json['prefProg'] if 'prefProg' in request.json else None
        avgSalary = request.json['avgSalary'] if 'avgSalary' in request.json else None
        uniRankingRangeStart = request.json['uniRankingRangeStart'] if 'uniRankingRangeStart' in request.json else None
        uniRankingRangeEnd = request.json['uniRankingRangeEnd'] if 'uniRankingRangeEnd' in request.json else None
        locationPref = request.json['locationPref'] if 'locationPref' in request.json else None

        if not id or not token or not finAidReq or not prefProg or not avgSalary or not uniRankingRangeStart or not uniRankingRangeEnd or not locationPref:
            return {
                "status_code": 400,
                "message": "id, token, finAidReq, prefProg, avgSalary, uniRankingRangeStart, uniRankingRangeEnd, locationPref are required"
            }, 400

        db = connect_to_mysql(config)
        if db is None:
            return {
                "status_code": 408,
                "message": "Error Connecting to Database. Request has timedout. Please contact Support"
            }, 408

        cursor = db.cursor()
        # check if the user is already exists in the profile
        query2 = 'SELECT token FROM profiles WHERE id =%s'
        cursor.execute(query2, [str(id)])
        token2 = cursor.fetchall()

        if not token2:
            return {
            "status_code": 400,
            "message": "This user does not have a profile in the system yet. Please save a profile first"
        }, 400

        # update profile
        cursor.execute("""
           UPDATE profiles
           SET token=%s, finAidReq=%s, prefProg=%s, avgSalary=%s, uniRankingRangeStart=%s, uniRankingRangeEnd=%s, locationPref=%s
           WHERE id=%s
        """, (token, finAidReq, prefProg, avgSalary, uniRankingRangeStart, uniRankingRangeEnd, locationPref, id))

        db.commit()

        db.close()

    except Exception as e:
        print(e)
        return {
            "status_code": 500,
            "message": "Error updating profile"
        }, 500

    return {
        "status_code": 200,
        "message": "Profile updated Successfully"
    }, 200

@app.route('/profile', methods=['GET'])
def get_profile():
    try:
        id = request.args.get('id') if 'id' in request.args else None
        token = request.headers.get("Authorization")

        if not id:
            return {
                "status_code": 400,
                "message": "No id given"
            }, 400

        db = connect_to_mysql(config)
        if db is None:
            return {
                "status_code": 408,
                "message": "Error Connecting to Database. Request has timedout. Please contact Support"
            }, 408

        cursor = db.cursor()
        # check if the user is already exists in the profile
        query = "SELECT * FROM profiles WHERE token=%s"
        cursor.execute(query, [token])
        the_doc = cursor.fetchall()

        if not the_doc:
            return {
                "status_code": 400,
                "message": "No Profile associated with this token"
            }, 400

        return {
            "status_code": 200,
            "message": "Profile retrieved successfully",
            "finAidReq": the_doc[0][2],
            "prefProg": the_doc[0][3],
            "avgSalary": the_doc[0][4],
            "uniRankingRangeStart": the_doc[0][5],
            "uniRankingRangeEnd": the_doc[0][6],
            "locationPref": the_doc[0][7]
        }, 200

    except Exception as e:
        print("error")
        print(e)
        return {
            "status_code": 500,
            "message": "Error retrieving profile"
        }, 500

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
