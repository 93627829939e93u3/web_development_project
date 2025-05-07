// login.js

document.getElementById('login-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Retrieve user data from localStorage
    const user = JSON.parse(localStorage.getItem(username));

    if (user && user.password === password) {
        alert('Login successful!');
        // Redirect to home page
        localStorage.setItem('currentUser', username);
        window.location.href = 'home.html';
    } else {
        alert('Invalid username or password!');
    }
});
