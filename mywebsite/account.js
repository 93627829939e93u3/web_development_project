window.onload = function() {
    const currentUser = localStorage.getItem('currentUser') || "User";
    document.getElementById('homeUsername').innerText = currentUser;

    // Load user data from localStorage (including profile photo)
    const user = JSON.parse(localStorage.getItem('user')) || {
        profilePhoto: "default-photo.jpg", // Default if no profile photo is set
        purchases: []
    };

    // Display user profile photo (either default or from localStorage)
    const profilePhoto = document.getElementById("profilePhoto");
    profilePhoto.src = user.profilePhoto;

    // Handle photo upload
    const uploadPhotoInput = document.getElementById("uploadPhoto");
    uploadPhotoInput.addEventListener("change", function(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                // Update the profile photo preview
                profilePhoto.src = e.target.result;

                // Save the photo to the user data in localStorage
                user.profilePhoto = e.target.result;
                localStorage.setItem('user', JSON.stringify(user));
            };
            reader.readAsDataURL(file);
        }
    });

    // Populate the shopping table with the user's purchase details
    const shoppingTableBody = document.querySelector("#shoppingTable tbody");
    
    // If no purchases, display a message
    if (user.purchases.length === 0) {
        const noPurchasesMessage = document.createElement('tr');
        noPurchasesMessage.innerHTML = `<td colspan="4">No purchases yet</td>`;
        shoppingTableBody.appendChild(noPurchasesMessage);
    } else {
        // If there are purchases, display them
        user.purchases.forEach(product => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${product.title}</td>
                <td>${product.quantity}</td>
                <td>₹${product.price}</td>
                <td>₹${product.price * product.quantity}</td>
            `;
            shoppingTableBody.appendChild(row);
        });
    }
};
document.addEventListener("DOMContentLoaded", function() {
    // Fetch user data from localStorage
    const user = JSON.parse(localStorage.getItem('user')) || {
        profilePhoto: "default-photo.jpg",
        purchases: []
    };

    const profilePhoto = document.getElementById("profilePhoto");
    profilePhoto.src = user.profilePhoto;

    const uploadPhotoInput = document.getElementById("uploadPhoto");
    uploadPhotoInput.addEventListener("change", function(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                profilePhoto.src = e.target.result;
                user.profilePhoto = e.target.result;
                localStorage.setItem('user', JSON.stringify(user));
            };
            reader.readAsDataURL(file);
        }
    });

    // Display user's purchase details
    const shoppingDetails = document.getElementById("shoppingTable").getElementsByTagName('tbody')[0];
    user.purchases.forEach(product => {
        const row = shoppingDetails.insertRow();
        row.innerHTML = `
            <td>${product.productName}</td>
            <td>${product.quantity}</td>
            <td>₹${product.price}</td>
            <td>₹${product.price * product.quantity}</td>
        `;
    });
});
