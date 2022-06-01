# Event Queue

Event Queue was developed on Mac OS X. This guide describes the setup of the development environment.

## Server Installation

```shell
# Install and start MariaDB service
brew install mariadb
brew services start mariadb

# Check the service has been loaded
brew services list
```

## Client Setup

Development was done in Visual Studio Code using Python 2.7.x. Setup the project's workspace and set the Python's path in the workspace settings.

1. Menu Code > Preferences > Settings
2. Select "Workspace Settings" tab
3. Search for `python.pythonPath` (or select Extensions > Python Configuration > Python Path)
4. Enter the path to your Homebrew Python interpreter (example: `/usr/local/homebrew/bin/python`)

## Client Installation

**NOTE:** You need to install the XCode Command Line Tools. You can try to use the command `xcode-select --install`. If that does not work, try to download the Command Line Tools directly from [Apple](https://developer.apple.com/download/more/).

```shell
pip install mysql-connector-repackaged
```

## MariaDB Administration

```shell
# (optional) Set the root password
# mysqladmin -u root password 'yourpassword'

# Connect to the console (with an empty password)
mysql -u root -p ''
```

## Create Database

```sql
CREATE DATABASE event
  CHARACTER SET = 'utf8'
  COLLATE = 'utf8_general_ci';
```

## Create Structure

```shell
mysql -u root -p event < struct.sql
```

## Database Stop

```shell
brew services stop mariadb
```

## Event Queue Web API

For the Event Queue API you need to install Python bottle:

```bash
pip install bottle
```

To run the web API locally uncomment the `run()` line in the `app.wsgi` file and type:

```bash
cd www
python app.wsgi
```

To enable debug mode, use:

```python
bottle.run(host='localhost', port=8080, debug=True)
```
