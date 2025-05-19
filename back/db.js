const mysql = require('mysql2');
require('dotenv').config();

const connection = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'deft10230219!',
    database: 'class' 
  });

connection.connect(err => {
  if (err) throw err;
  console.log('✅ MySQL 연결 성공쓰~');
});

module.exports = connection;