from flask_mysqldb import MySQL

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'smart_brewery'
app.config['MYSQL_HOST'] = 'localhost'

mysql = MySQL(app)