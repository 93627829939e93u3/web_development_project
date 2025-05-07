// Load products from localStorage or initialize an empty array
let products = JSON.parse(localStorage.getItem('products')) || [];
let cart = JSON.parse(localStorage.getItem('cart')) || [];

// Function to load and display products
function loadProducts() {
    const productList = document.getElementById('product-list');
    productList.innerHTML = '';

    products.forEach(product => {
        const productItem = document.createElement('div');
        productItem.classList.add('product-item');
        productItem.innerHTML = `
            <img src="${product.imageUrl}" alt="${product.title}">
            <h3>${product.title}</h3>
            <p>MRP: ₹${product.mrp}</p>
            <p>Price: ₹${product.price}</p>
            <button onclick="addToCart(${product.id})">Add to Cart</button>
        `;
        productList.appendChild(productItem);
    });
}

// Function to add a product to the cart or update its quantity
function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    if (product) {
        const existingProduct = cart.find(item => item.id === productId);
        if (existingProduct) {
            existingProduct.quantity += 1; // Increment quantity if the product already exists in the cart
        } else {
            product.quantity = 1; // Set initial quantity to 1 for new products
            cart.push(product);
        }
        localStorage.setItem('cart', JSON.stringify(cart));
        
        updateCart();
        updateCartCount();
    }
}

// Function to calculate the total price based on product quantities
function calculateTotal() {
    return cart.reduce((total, product) => total + product.price * product.quantity, 0);
}

// Function to update the cart display
function updateCart() {
    const cartItemsContainer = document.getElementById('cart-items');
    const cartTotal = document.getElementById('cart-total');

    cartItemsContainer.innerHTML = '';
    cart.forEach((item, index) => {
        const cartItem = document.createElement('div');
        cartItem.classList.add('cart-item');
        cartItem.innerHTML = `
            <img src="${item.imageUrl}" alt="${item.title}">
            <h3>${item.title}</h3>
            <p>Price: ₹${item.price}</p>
            <div class="quantity-controls">
                <button onclick="changeQuantity(${index}, -1)">-</button>
                <span>${item.quantity}</span>
                <button onclick="changeQuantity(${index}, 1)">+</button>
            </div>
            <button class="delete-button" onclick="deleteProduct(${index})">Delete</button>
        `;
        cartItemsContainer.appendChild(cartItem);
    });

    cartTotal.textContent = `Total: ₹${calculateTotal()}`;
}

// Function to change the quantity of a product in the cart
function changeQuantity(index, delta) {
    if (cart[index]) {
        cart[index].quantity += delta;
        if (cart[index].quantity <= 0) {
            cart.splice(index, 1); // Remove item from cart if quantity is 0 or less
        }
        localStorage.setItem('cart', JSON.stringify(cart));
        updateCart();
        updateCartCount();
    }
}

// Function to delete a product from the cart
function deleteProduct(index) {
    if (cart[index]) {
        cart.splice(index, 1); // Remove the product from the cart
        localStorage.setItem('cart', JSON.stringify(cart));
        updateCart();
        updateCartCount();
    }
}

// Function to update and display the cart count
function updateCartCount() {
    const cartCount = document.getElementById('cart-count');
    cartCount.textContent = cart.length;
}
// Function to check out and complete the purchase
function checkOut() {
    if (cart.length === 0) {
        alert('Your cart is empty! Please add products to your cart before checking out.');
        return;
    }
    alert('Thank you for your purchase! Your order has been placed.');
    clearCart(); // Clear the cart after checkout
}

// Function to clear all products from the cart and localStorage
function clearCart() {
    cart = []; // Clear the cart array
    localStorage.removeItem('cart'); // Remove cart from localStorage
    updateCart(); // Update the cart display
    updateCartCount(); // Update the cart count
}
document.querySelectorAll(".add-to-cart").forEach(button => {
    button.addEventListener("click", function() {
        const productName = this.dataset.productName;
        const price = parseFloat(this.dataset.price);
        const quantity = 1; // Default quantity

        let purchases = JSON.parse(localStorage.getItem("purchases")) || [];
        purchases.push({ productName, quantity, price });
        localStorage.setItem("purchases", JSON.stringify(purchases));

        alert("Product added to cart!");
    });
});

// Function to toggle the cart visibility
function toggleCart() {
    const cartSection = document.getElementById('cart-section');
    cartSection.style.display = cartSection.style.display === 'none' ? 'block' : 'none';
}
// Function to check out and redirect to the checkout page
function checkOut() {
    if (cart.length === 0) {
        alert('Your cart is empty! Please add products to your cart before checking out.');
        return;
    }
    // Save the cart details to localStorage for use on the checkout page
    localStorage.setItem('checkoutCart', JSON.stringify(cart));
    // Redirect to the checkout page
    window.location.href = 'checkout.html';
}

// Function to close the cart
function closeCart() {
    document.getElementById('cart-section').style.display = 'none';
}

// Initial load
loadProducts();
updateCart();
updateCartCount();

// Clear all data from localStorage
// localStorage.clear();
