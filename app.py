from flask import Flask
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from flask import request, abort
from config import MONGO_DB_CONNECTION_STRING

client = MongoClient(MONGO_DB_CONNECTION_STRING)
db = client['grade-logging-api']
GRADE = db['grade']
TOKEN = db['token']
TEAM = db['team']

app = Flask(__name__)


def api_key_middleware():
    if request.endpoint in ['signUp']: return
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
    the_doc = TOKEN.find_one({
        "utorid": utorid
    })

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

        the_doc = GRADE.find_one({
            "utorid": utorid,
            "course": course
        })
        if the_doc:
            return {
                "status_code": 400,
                "message": "Grade already exists"
            }, 400
        grade_id = GRADE.insert_one({
            "utorid": utorid,
            "course": course,
            "grade": grade
        }).inserted_id
        return {
            "status_code": 200,
            "message": "Grade created successfully",
            "id": str(grade_id)
        }, 200
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
        the_doc = GRADE.find_one({
            "utorid": utorid,
            "course": course
        })
        if not the_doc:
            return {
                "status_code": 404,
                "message": "Grade not found"
            }, 404
        return {
            "status_code": 200,
            "message": "Grade retrieved successfully",
            "utorid": the_doc['utorid'],
            "grade": the_doc['grade']
        }, 200
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

        the_doc = GRADE.find_one({
            "utorid": utorid,
            "course": course
        })
        if not the_doc:
            return {
                "status_code": 404,
                "message": "The grade does not exist, please create it first using POST /grade"
            }
        
        GRADE.update_one({
            "_id": the_doc['_id']
        }, {
            "$set": {
                "grade": grade
            }
        })
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

        the_doc = GRADE.find_one({
            "utorid": utorid,
            "course": course
        })
        if not the_doc:
            return {
                "status_code": 404,
                "message": "The grade does not exist, there's no need to delete it."
            }
        
        GRADE.delete_one({
            "_id": the_doc['_id']
        })
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

import random
import string
@app.route('/signUp', methods=['GET'])
def signUp():
    # get parameters from request
    utorid = request.args.get('utorid') if 'utorid' in request.args else None

    # generate a random api token.
    # generate deployment api token.

    # first, see if this utorid is associated with a token.
    the_doc = TOKEN.find_one({
        "utorid": utorid
    })
    if the_doc:
        return {
            "status_code": 200,
            "message": "Token generated successfully",
            "token": the_doc['token']
        }
    def generate_token(length=32):
        # Define the characters that can be used in the token
        characters = string.ascii_letters + string.digits

        # Generate a random token using the specified length
        token = ''.join(random.choice(characters) for _ in range(length))

        return token

    token = generate_token()

    # save to DB.
    TOKEN.insert_one({
        "utorid": utorid,
        "token": token
    })

    # return with token
    return {
        "status_code": 200,
        "message": "Token generated successfully",
        "token": token
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

    # check if the team already exists.
    the_doc = TEAM.find_one({
        "name": name
    })
    if the_doc:
        return {
            "status_code": 400,
            "message": "Team already exists"
        }, 400

    # check if the utorid is already in a team.
    the_doc = TEAM.find_one({
        "members": {"$in": [utorid]}
    })
    if the_doc:
        return {
            "status_code": 400,
            "message": "You are already in a team"
        }, 400
    
    # create a team.
    TEAM.insert_one({
        "name": name, 
        "members": [utorid]
    })

    return {
        "status_code": 200,
        "message": f'Team {name} created successfully'
    }, 200



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=20112, debug=True, threaded=True)
