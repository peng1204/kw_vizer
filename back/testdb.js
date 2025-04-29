// const mysql = require('mysql2');

// const connection = mysql.createConnection({
//     host: 'localhost',
//     user: 'root',
//     password: 'deft10230219!',
//     database: 'class' 
//   });
  

// connection.connect((err) => {
//   if (err) {
//     console.error('MySQL 연결 실패:', err);
//     return;
//   }
//   console.log('MySQL 연결 성공!');

//   connection.query(
//     "SELECT * FROM classscore WHERE grade = '보통'",
//     (error, results, fields) => {
//       if (error) throw error;
//       console.log('결과:', results);
//     }
//   );
// });