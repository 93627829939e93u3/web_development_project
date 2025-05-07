// Load cart details from localStorage
let checkoutCart = JSON.parse(localStorage.getItem('checkoutCart')) || [];


// Function to display cart details on the checkout page
function loadCheckoutItems() {
    const checkoutItemsContainer = document.getElementById('checkout-items');
    const checkoutTotal = document.getElementById('checkout-total');

    checkoutItemsContainer.innerHTML = ''; // Clear previous content
    let totalAmount = 0;
    let totalQuantity = 0;

    checkoutCart.forEach(item => {
        const checkoutItem = document.createElement('div');
        checkoutItem.classList.add('checkout-item');
        checkoutItem.innerHTML = `
            <img src="${item.imageUrl}" alt="${item.title}"><br>
            <h3>${item.title}</h3><br>
            <p>Price: ₹${item.price}</p><br>
            <p>Quantity: ${item.quantity}</p><br>
            <button class="remove-item" data-id="${item.id}">Remove</button>
        `;
        checkoutItemsContainer.appendChild(checkoutItem);
        totalAmount += item.price * item.quantity;
        totalQuantity += item.quantity;
    });

    checkoutTotal.textContent = `Total: ₹${totalAmount} (${totalQuantity} items)`;

    // Add event listeners to remove item buttons
    const removeItemButtons = document.querySelectorAll('.remove-item');
    removeItemButtons.forEach(button => {
        button.addEventListener('click', () => {
            const itemId = button.getAttribute('data-id');
            checkoutCart = checkoutCart.filter(item => item.id !== itemId);
            localStorage.setItem('checkoutCart', JSON.stringify(checkoutCart));
            loadCheckoutItems(); // Refresh the checkout page
        });
    });
}
function loadCheckoutItems() {
    const checkoutItemsContainer = document.getElementById('checkout-items');
    const checkoutTotal = document.getElementById('checkout-total');

    checkoutItemsContainer.innerHTML = ''; // Clear previous content
    let totalAmount = 0;
    let totalQuantity = 0;

    if (checkoutCart.length === 0) {
        // If the cart is empty, show a message
        checkoutItemsContainer.innerHTML = '<p class="empty-cart-message">No items in the cart. All products have been removed.</p>';
        checkoutTotal.textContent = 'Total: ₹0 (0 items)';
        return; // Exit the function
    }

    checkoutCart.forEach(item => {
        const checkoutItem = document.createElement('div');
        checkoutItem.classList.add('checkout-item');
        checkoutItem.innerHTML = `
            <img src="${item.imageUrl}" alt="${item.title}">
            <h3>${item.title}</h3>
            <p>Price: ₹${item.price}</p>
            <p>Quantity: ${item.quantity}</p>
            <button class="remove-item" data-id="${item.id}">Remove</button>
        `;
        checkoutItemsContainer.appendChild(checkoutItem);
        totalAmount += item.price * item.quantity;
        totalQuantity += item.quantity;
    });

    checkoutTotal.textContent = `Total: ₹${totalAmount} (${totalQuantity} items)`;

    // Add event listeners to remove item buttons
    const removeItemButtons = document.querySelectorAll('.remove-item');
    removeItemButtons.forEach(button => {
        button.addEventListener('click', () => {
            const itemId = button.getAttribute('data-id');

            // Ensure itemId matches item.id type
            checkoutCart = checkoutCart.filter(item => item.id.toString() !== itemId);

            // Update localStorage and refresh the checkout page
            localStorage.setItem('checkoutCart', JSON.stringify(checkoutCart));
            loadCheckoutItems(); // Refresh the checkout page
        });
    });
}


// Function to complete the purchase and update user account
// Function to handle the complete purchase action
function completePurchase() {
    if (checkoutCart.length === 0) {
        // If there are no items in the cart, show an alert
        alert("No products found. Please add items to your cart before completing the purchase.");
        return; // Exit the function
    }

    // Add your logic here for processing the purchase
    // For example, redirect to a payment page or show a success message
    alert("Thank you for your purchase! Your order is being processed.");
    // Clear the cart after purchase
    checkoutCart = [];
    localStorage.setItem('checkoutCart', JSON.stringify(checkoutCart));
    loadCheckoutItems(); // Refresh the checkout page
}

// Add an event listener to the "Complete Purchase" button
const completePurchaseButton = document.getElementById('complete-purchase');
if (completePurchaseButton) {
    completePurchaseButton.addEventListener('click', completePurchase);
}


// Initial load of checkout items
loadCheckoutItems();

// Attach event listener to the complete purchase button
document.getElementById('completePurchaseButton').addEventListener('click', completePurchase);
