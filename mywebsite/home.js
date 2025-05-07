let users = JSON.parse(localStorage.getItem('users')) || [];

function signup() {
    const username = document.getElementById('signupUsername').value.trim();
    const email = document.getElementById('signupEmail').value.trim();
    const password = document.getElementById('signupPassword').value.trim();

    if (username && email && password) {
        const existingUser = users.find(u => u.username === username || u.email === email);
        if (existingUser) {
            alert('Username or email already exists.');
        } else {
            users.push({ username, email, password });
            localStorage.setItem('users', JSON.stringify(users));
            alert('Signup successful! Please login.');
            window.location.href = 'login.html';
        }
    } else {
        alert('Please fill out all fields.');
    }
}

function login() {
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value.trim();

    const user = users.find(u => u.username === username && u.password === password);
    if (user) {
        localStorage.setItem('currentUser', username);
        window.location.href = 'home.html';
    } else {
        alert('Invalid username or password.');
    }
}

function logout() {
    localStorage.removeItem('currentUser');
    window.location.href = 'login.html';
}

window.onload = function() {
    const currentUser = localStorage.getItem('currentUser');
    if (window.location.pathname.includes('home.html') && currentUser) {
        document.getElementById('homeUsername').innerText = currentUser;
    } else if (window.location.pathname.includes('dashboard.html')) {
        populateUserTable();
    } else if (!currentUser && !window.location.pathname.includes('signup.html') && !window.location.pathname.includes('login.html')) {
        window.location.href = 'login.html';
    }
};

function populateUserTable() {
    const tableBody = document.getElementById('userTable');
    tableBody.innerHTML = '';
    users.forEach((user, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${index + 1}</td><td>${user.username}</td><td>${user.email}</td>`;
        tableBody.appendChild(row);
    });
}