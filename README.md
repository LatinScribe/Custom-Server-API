# Custom-Server-API

## Overview
An API that handles data storage and retrieval requests to our server. Python based using flask, and implements a mySQL database. 

This API is based off the grade-logging API developed by [Chen Pan](https://github.com/ChenPanXYZ?tab=repositories).

## API Documentation (How to use it)

Link to access API: https://henrytchen.com/custom-api/

**Note: Please refer to documentation of AUTH Header requirements!

Features:
1) [Sign Up](#sign-up)
2) [Record A Grade](#record-a-grade)
3) [Get A Grade](#get-a-grade)

### Sign up

The API to sign up a "UTORid" (username) for this system.

Note:
1. Even though we call it "UTORid", you don't have to sign up with your real UTORid.
You can use any ids you want, if not taken by someone else already.
2. You need to copy and paste the returned token immediately.
The token will only be shown once. If you forget the token, you need to sign up with
a different id.

**URL** : `/signUp`

**Method** : `GET`

**Auth required** : Not required to signup

**Required Request Parameters**
```json
{
    "utorid": "The ID (doesn't have to be your real utorid)"
}
```
#### Success Responses

**Condition** :  The utorid has not previously been used to signup for the system.

**Code** : `200 OK`

**Content example** :

```json
{
    "status_code": 200,
    "message": "Token generated successfully",
    "token": "UNIQUE_API_TOKEN_FOR_THIS_USERNAME"
}
```

#### Error Response

##### UTORid not available.

**Condition** : Someone has signed up with this utorid already.

**Content example** :

```json
{
    "status_code": 200,
    "message": "Someone took this username. If you are not the owner of this username or you forgot your token, please sign up with a different username and use the new token instead."
}
```

### Record a grade

Record a grade of a course for a utorid.

**URL** : `/grade`

**Method** : `POST`

**Auth required** : Required in header `Authorization`.

**Required Request Body**
```json
{
    "course": "The course code",
    "grade": "The grade to log"
}
```
#### Success Responses

**Condition** : Access to the utorid is verified by the authorization token, and a grade for the course has not been logged before.

**Code** : `200 OK`

**Content example** : 

```json
{
    "id": "64b85b6ce66b09ca82769e68",
    "message": "Grade created successfully",
    "status_code": 200
}
```

#### Error Response

##### Grade already exists.

**Condition** : The grade of this course for this student has already been logged.

**Code** : `400 BAD REQUEST`

**Content example** :

```json
{
    "message": "Grade already exists",
    "status_code": 400
}
```

##### Grade is not valid.

**Condition** : The grade is not an integer between 0 - 100.

**Code** : `400 BAD REQUEST`

**Content example** :

```json
{
    "message": "grade must be an integer between 0 and 100",
    "status_code": 400
}
```

##### API Token is invalid

**Condition** : The given authorization token doesn't match with the ones that have the access to the utorid. Or the authorization token doesn't exist.
See the documentation for signUp for how to get a token.

**Code** : `401`

**Content example** :

```json
{
    "message": "Invalid token",
    "status_code": 401
}
```

##### Server Error

**Condition** : The backend server has an issue.

**Code** : `500 Internal Server Error`

**Content example** :

```json
{
   "status_code": 500,
   "message": "Error retrieving grade"
}, 500
```

### Get a grade

Get a grade for a course for a specific UTORid. One can only access grades for themselves or the others in the same team.

**URL** : `/grade`

**Method** : `GET`

**Auth required** : Required in header `Authorization`.

**Required Request Parameters**
```json
{
    "utorid": "The utorid",
    "course": "The course code"
}
```
#### Success Responses

**Condition** : Access to the utorid's grades is verified by the authorization token, and a grade for the course has been logged before.

**Code** : `200 OK`

**Content example** :

```json
{
  "grade": {
    "_id": {
      "$oid": "64b85b05e66b09ca82769e67"
    },
    "course": "CSC207",
    "grade": 85,
    "utorid": "t1chenpa"
  },
  "message": "Grade retrieved successfully",
  "status_code": 200,
  "utorid": "t1chenpa"
}
```

#### Error Response

##### Grade not found.

**Condition** : The grade of this course for this given utorid doesn't exist.

**Code** : `404 NOT FOUND`

**Content example** :

```json
{
    "message": "Grade not found",
    "status_code": 404
}
```

##### API Token is invalid

**Condition** : The given authorization token doesn't match with the ones that have the access to the utorid.
Or the authorization token doesn't exist. See the documentation for signUp for how to get a token.

**Code** : `401`

**Content example** :

```json
{
    "message": "Invalid token",
    "status_code": 401
}
```

##### Server Error

**Condition** : The backend server has an issue.

**Code** : `500 Internal Server Error`

**Content example** :

```json
{
   "status_code": 500,
   "message": "Error retrieving grade"
}
```
