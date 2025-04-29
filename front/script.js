document.querySelector('.login-form').addEventListener('submit', function (e) {
  e.preventDefault(); //기본 이동을 막는 부분분

  const class_number = document.querySelector('#class_number').value;
  const password = document.querySelector('#password').value;

  fetch('/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ class_number, password })
  })
    .then((res) => {
      if (!res.ok) throw res;
      return res.json();
    })
    .then((data) => {
      if (data.success) {
        window.location.href = '/home.html'; // 로그인 성공 시 이동
      } else {
        alert(data.message || '로그인 실패');
      }
    })
    .catch((err) => {
      console.error('로그인 오류', err);
      alert('서버 오류');
    });
});
