# Custom-Server-API

## Overview
An API that handles data storage and retrieval requests to our server. Python based using flask, and implements a mySQL database. 

This API is based off the MongolDB grade-logging API developed by [Chen Pan](https://github.com/ChenPanXYZ?tab=repositories).

Checkout our full project at: https://github.com/LatinScribe/UniversityExplorer 

## API Documentation (How to use it)

Link to access API: https://henrytchen.com/custom-api/

Use the link to make relevant HTTP requests!

**Note: Please refer to documentation of AUTH Header requirements!

Features:
1) [Sign Up](#sign-up)
2) [Sign In](#sign-in)
3) [Exists by Name](#exists-by-name)
4) [Save Profile](#save-a-profile)
5) [Update Profile](#update-a-profile)

Planned Features:

4) Password Reset
   
6) Token Reset

9) Profile data - creation + retrieve

---

### Sign up

The API to sign up a user for this system (with the given username and password).

Note:
1. Username can be any string (currently no rules), if not taken by someone else already.
2. It might be helpful to copy and paste or save the returned token immediately (you will likely need this again later on).
The token will also be shown on sign-in. It is recommended that the same be done with the returned id.

**URL** : `/signUp`

**Method** : `GET`

**Auth required** : Not required to signup

**Required Request Parameters**
```json
{
    "username": "The username chosen",
    "password": "The password chosen",
}
```
#### Success Responses

**Condition** :  The username has not previously been used to signup for the system.

**Code** : `200 OK`

**Content example** :

```json
{
    "id": 1234,
    "status_code": 200,
    "message": "Token generated successfully",
    "token": "UNIQUE_API_TOKEN_FOR_THIS_USERNAME"
}
```

#### Error Response

##### Username not available.

**Condition** : Someone has signed up with this username already.

**Content example** :

```json
{
    "status_code": 200,
    "message": "USERNAME ALREADY EXISTS"
}
```

##### No Username or Password Given

**Condition** : Either (or both) the username or password were not passed correctly in the request.

**Code** : `400 BAD REQUEST`

**Content example** :

```json
{
   "status_code": 400,
   "message": "NO PASSWORD or USERNAME GIVEN"
}
```

---

### Sign In

The API to sign in with a username and password to the system.

Note:
1.  It might be helpful to copy and paste or save the returned token immediately (you will likely need this again later on)

**URL** : `/signIn`

**Method** : `GET`

**Auth required** : Not required to signup

**Required Request Parameters**
```json
{
    "username": "The username chosen",
    "password": "The password chosen",
}
```
#### Success Responses

**Condition** :  The username and password matches the associated user data on the server.

**Code** : `200 OK`

**Content example** :

```json
{
    "id": 1234,
    "status_code": 200,
    "message": "SIGN IN SUCESSFUL",
    "token": "UNIQUE_API_TOKEN_FOR_THIS_USERNAME"
}
```

#### Error Response

##### No Username or Password Given

**Condition** : Either (or both) the username or password were not passed correctly in the request.

**Code** : `400 BAD REQUEST`

**Content example** :

```json
{
   "status_code": 400,
   "message": "NO PASSWORD or USERNAME GIVEN"
}
```

##### Given Username or Password is incorrect

**Condition** : Either (or both) the username or password were incorrect or incorrectly passed in the request.

**Code** : `400 BAD REQUEST`

**Content example** :

```json
{
   "status_code": 400,
   "message": "PASSWORD OR USERNAME INCORRECT"
}
```

---

### Exists by Name

The API to check if a username is already in the system.

**URL** : `/existsByName`

**Method** : `GET`

**Auth required** : Not required

**Required Request Parameters**
```json
{
    "username": "The username to check"
}
```
#### Success Responses

**Condition** :  No errors were thrown in checking

**Code** : `200 OK`

**Content example** :

```json
{
    "status_code": 200,
    "message": "USER DOES NOT EXIST or USER EXISTS"
}
```

#### Error Response

##### No Username 

**Condition** : Username was not passed correctly in the request.

**Code** : `400 BAD REQUEST`

**Content example** :

```json
{
   "status_code": 400,
   "message": "NO USERNAME GIVEN"
}
```

---

### Save a profile

The API to save a profile to a given user.

Note:
1. This function should only be used to save the initial/first profile. If the user already
has a profile in the system associated to their account, the updateProfile API should be used instead

**URL** : `/saveProfile`

**Method** : `POST`

**Auth required** : Required in header `Authorization`.

**Required Request Body**
```json
{
    "id": "The user's account id",
    "finAidReq": "The finantial aid required by the user",
    "prefProg": "The prefered program selected by user",
    "avgSalary": "The post-graduate desire salary selected by the user",
    "uniRankingRangeStart": "The beginning of the range of desired College ranking",
    "uniRankingRangeEnd": "The end of the range of desired College ranking",
    "locationPref": "The prefered location selected by the user"
}
```
#### Success Responses

**Condition** : Access to the account is verified by the authorization token, and a profile for the user has not been saved before.

**Code** : `200 OK`

**Content example** : 

```json
{
    "message": "Profile Saved Successfully",
    "status_code": 200
}
```

#### Error Response

##### Profile associated to this user already exists.

**Condition** : A profile for this user has already been created.

**Code** : `400 BAD REQUEST`

**Content example** :

```json
{
    "message": "This user already has a profile in the system. If you want to moddify the profile, please use updateProfile instead",
    "status_code": 400
}
```

##### Incorrect or missing request body paraameters

**Condition** : Failed to correctly provide the required request body parameters

**Code** : `400 BAD REQUEST`

**Content example** :

```json
{
    "message": "id, token, finAidReq, prefProg, avgSalary, uniRankingRangeStart, uniRankingRangeEnd, locationPref are required",
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
   "message": "Error saving profile"
}, 500
```

---

### Update a profile

The API to update the profile of a given user.

Note:
1. This function should only be used after a profile has already been saved for the given user.
If the user does not have a profile yet, the saveProfile API should be used instead. 

**URL** : `/updateProfile`

**Method** : `PUT`

**Auth required** : Required in header `Authorization`.

**Required Request Body**
```json
{
    "id": "The user's account id",
    "finAidReq": "The finantial aid required by the user",
    "prefProg": "The prefered program selected by user",
    "avgSalary": "The post-graduate desire salary selected by the user",
    "uniRankingRangeStart": "The beginning of the range of desired College ranking",
    "uniRankingRangeEnd": "The end of the range of desired College ranking",
    "locationPref": "The prefered location selected by the user"
}
```
#### Success Responses

**Condition** : Access to the account is verified by the authorization token, and a profile for the given user exists.

**Code** : `200 OK`

**Content example** : 

```json
{
    "message": "Profile updated Successfully",
    "status_code": 200
}
```

#### Error Response

##### No Profile associated to this user.

**Condition** : A profile for this user has not yet been created.

**Code** : `400 BAD REQUEST`

**Content example** :

```json
{
    "message": "This user does not have a profile in the system yet. Please save a profile first",
    "status_code": 400
}
```

##### Incorrect or missing request body paraameters

**Condition** : Failed to correctly provide the required request body parameters

**Code** : `400 BAD REQUEST`

**Content example** :

```json
{
    "message": "id, token, finAidReq, prefProg, avgSalary, uniRankingRangeStart, uniRankingRangeEnd, locationPref are required",
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
   "message": "Error updating profile"
}, 500
```

---

### Retrieve a profile

The API to retrieve the profile of a given user.

Note:
1. This function should only be used after a profile has already been saved for the given user.
If the user does not have a profile yet, the saveProfile API should be used instead. 

**URL** : `/profile`

**Method** : `GET`

**Auth required** : Required in header `Authorization`.

**Required Request Body**
```json
{
    "id": "The user's account id"
}
```
#### Success Responses

**Condition** : Access to the account is verified by the authorization token, and a profile exists for the given user.

**Code** : `200 OK`

**Content example** : 

```json
{
    "message": "Profile retrieved successfully",
    "finAidReq": "The finantial aid required by the user",
    "prefProg": "The prefered program selected by user",
    "avgSalary": "The post-graduate desire salary selected by the user",
    "uniRankingRangeStart": "The beginning of the range of desired College ranking",
    "uniRankingRangeEnd": "The end of the range of desired College ranking",
    "locationPref": "The prefered location selected by the user"
    "status_code": 200
}
```

#### Error Response

##### No Profile associated to this user.

**Condition** : A profile for this user has not yet been created.

**Code** : `400 BAD REQUEST`

**Content example** :

```json
{
    "message": "No Profile associated with this token",
    "status_code": 400
}
```

##### Incorrect or missing request body paraameters

**Condition** : Failed to correctly provide the id in the request body

**Code** : `400 BAD REQUEST`

**Content example** :

```json
{
    "message": "No id given",
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
   "message": "Error retrieving profile"
}, 500
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
---
### General Errors
##### Database Connection Error (general)
**Condition** : Error in connecting to database during http request.

**Code** : `400`

**Content example** :

```json
{
   "status_code": 400,
   "message": "Error Connecting to Database. Request has timedout. Please contact Support"
}
```

##### Database Connection Error (middleware)
**Condition** : Error in connecting to the database in the middleware processing.

**Code** : `401`

**Content example** :

```json
{
   "status_code": 401,
   "message": "Error Connecting to Database"
}
```


Author: Henry TJ Chen

Questions? Want to implement this for your own project? Reach out to me!
