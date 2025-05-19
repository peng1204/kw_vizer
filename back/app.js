const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');
const { answer_query } = require('./chatbot/answer_query');
const db = require('./db');

const app = express();
const PORT = 3000;

app.use(cors());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, '../front')));

// 🔍 챗봇 질의 처리
app.post('/chat', async (req, res) => {
  const { message, class_number } = req.body;

  if (!message || !class_number) {
    return res.status(400).json({ error: '질문과 학번이 모두 필요합니다.' });
  }

  try {
    const response = await answer_query(message, class_number);
    res.json({ response });
  } catch (error) {
    console.error('챗봇 오류:', error);
    res.status(500).json({ error: '답변 생성 중 오류가 발생했습니다.' });
  }
});

// 🔐 로그인 처리 및 이름 전달
app.post('/login', (req, res) => {
  const { class_number, password } = req.body;

  const query = 'SELECT * FROM studentinform WHERE id = ? AND password = ?';
  db.query(query, [class_number, password], (err, results) => {
    if (err) {
      console.error('DB 오류:', err);
      return res.status(500).send('DB 오류');
    }
    if (results.length > 0) {
      const user = results[0];
      res.json({
        success: true,
        class_number: user.id,
        name: user.name
      });
    } else {
      res.status(401).json({ success: false, message: '학번 또는 비밀번호가 올바르지 않습니다.' });
    }
  });
});

app.listen(PORT, () => {
  console.log(`✅ Node.js 서버 실행 중: http://localhost:${PORT}`);
});
