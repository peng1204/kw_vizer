const express = require('express');
const router = express.Router();
const db = require('../db');

router.post('/login', (req, res) => {
  const { class_number, password } = req.body;

  const query = 'SELECT * FROM studentinform WHERE id = ? AND password = ?';
  db.query(query, [class_number, password], (err, results) => {
    if (err) return res.status(500).send('DB 오류');
    if (results.length > 0) {
      const user = results[0];
      res.json({ success: true, name: user.name });
    } else {
      res.json({ success: false });
    }
  });
});

module.exports = router;
