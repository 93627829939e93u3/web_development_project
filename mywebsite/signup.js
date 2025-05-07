// signup.js

document.getElementById('signup-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    // Check if user already exists
    if (localStorage.getItem(username)) {
        alert('Username already exists! Please choose another one.');
    } else {
        // Save user data in localStorage
        const user = { email, password };
        localStorage.setItem(username, JSON.stringify(user));
        alert('Signup successful! Please login.');
        // Redirect to login page
        window.location.href = 'login.html';
    }
});
function signup() {
    const username = document.getElementById('signupUsername').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;

    if (username && email && password) {
        users.push({ username, email, password });
        localStorage.setItem('users', JSON.stringify(users));
        alert('Signup successful! Please login.');
        window.location.href = 'login.html';
    } else {
        alert('Please fill out all fields.');
    }
}
document.getElementById("signup-form").addEventListener("submit", function(event) {
    event.preventDefault();

    const user = {
        indexNumber: Date.now(), // Unique index using timestamp
        name: document.getElementById("name").value,
        contact: document.getElementById("contact").value
    };

    localStorage.setItem("user", JSON.stringify(user));
    window.location.href = "dashboard.html"; // Redirect to dashboard
});

