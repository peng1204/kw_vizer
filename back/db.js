const mysql = require('mysql2');
require('dotenv').config();

const connection = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'deft10230219!',
    database: 'class' 
  });
  
db.connect(err => {
    if (err) throw err;
    console.log('✅ MySQL 연결 성공쓰쓰');
  });
  
  module.exports = db;