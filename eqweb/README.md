# Event Queue Web

## Description

A "rich" web interface to the Event Queue.

![Event Queue web interface](docs/eqweb.png)

## Database

Refer to the the `database/struct.sql` for the database structure.

## Configuration

Change the following configuration settings to match your environment:

```python
# Secret key to encrypt session variables
SECRET_KEY = '<enter some random string here>'

# If result is paginated, how many items to display per page
PER_PAGE = 50

# SQL Alchemy connection URI
SQLALCHEMY_DATABASE_URI = 'mysql://dbuser:dbpass@dbhost:3306/event'
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

## TODO

A list of missing options that would be nice to have:

- Enter the password twice when creating a new account (sign-up)
- Request an email confirmation when creating a new account (sign-up)
- Update profile (name, email and password)
- Graph search results

## Contributors

- [Jorge Morgado](https://github.com/jorgemorgado) (Author)

## License

Released under the [MIT License](http://www.opensource.org/licenses/MIT).
