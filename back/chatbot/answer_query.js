// back/chatbot/answer_query.js

const { spawn } = require('child_process');

async function answer_query(userInput, classNumber) {
  return new Promise((resolve, reject) => {
    const process = spawn('python', ['back/chatbot/query_chroma.py', userInput]);

    // 🔥 여기가 중요합니다!
    process.stdout.setEncoding('utf8');
    process.stderr.setEncoding('utf8');

    let result = '';

    process.stdout.on('data', (data) => {
      result += data.toString();
    });

    process.stderr.on('data', (data) => {
      console.error('Python 오류:', data.toString());
    });

    process.on('close', () => {
      resolve(result.trim());
    });
  });
}

module.exports = { answer_query };
