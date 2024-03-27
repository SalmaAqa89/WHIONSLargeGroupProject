# Team *WHIONS* Large Group project

## Team members
The members of the team are:
- *Hannah Ishimwe*
- *Salma Aqarrout*
- *Onyiyechukwu Dozie*
- *Ishika Arora*
- *Najla Shainan*
- *Wanzhen Wang*

## Project structure
The project is called `Bloom`.  It currently consists of a single app `tasks`.

## Deployed version of the application
The deployed version of the application can be found at [*https://whions-final-a9df8eb9c312.herokuapp.com*](*https://whions-final-a9df8eb9c312.herokuapp.com*).
First user:
    username: @johndoe
    password: Password123
Second user:
    username: @janedoe
    password: Password123

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

*The above instructions should work in your version of the application.  If there are deviations, declare those here in bold.  Otherwise, remove this line.*

## Sources
The packages used by this application are specified in `requirements.txt`

*Declare are other sources here, and remove this line*
# WHIONSLargeGroupProject
