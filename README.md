# Custom-Server-API

## Overview
This API handles data storage and retrieval request to our server. It is Python based using flask, and implements a mySQL database. 

This API is based off the grade-logging API developed by [Chen Pan](https://github.com/ChenPanXYZ?tab=repositories).

## API Documentation (How to use it)

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
