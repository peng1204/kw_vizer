const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const PORT = 3000;

// 미들웨어 설정
app.use(cors());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// MySQL 연결 설정
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'deft10230219!',
    database: 'class' 
});

// 연결 확인
db.connect((err) => {
  if (err) {
    console.error('DB 연결 실패:', err);
  } else {
    console.log('MySQL 연결 성공');
  }
});

// 프론트엔드 정적 파일 서빙
app.use(express.static(path.join(__dirname, '../front')));

// JSON 및 폼 데이터 파싱
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.post('/login', (req, res) => {
    const { class_number, password } = req.body;
  
    const query = 'SELECT * FROM studentinform WHERE id = ? AND password = ?';
    db.query(query, [class_number, password], (err, results) => {
      if (err) {
        console.error('쿼리 오류:', err);
        res.status(500).send('서버 오류');
      } else if (results.length > 0) {
        // 로그인 성공 시 JSON 응답, home 페이지로 이동하게끔 
        res.json({ success: true });
      } else {
        res.status(401).json({ success: false, message: '학번 또는 비밀번호가 틀렸습니다.' });
      }
    });
  });

// 기본 페이지 제공
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../front/index.html'));
});

// 서버 실행
app.listen(PORT, () => {
  console.log(`서버 실행 중: http://localhost:${PORT}`);
});
