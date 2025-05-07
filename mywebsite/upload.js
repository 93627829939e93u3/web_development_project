// upload.js

let products = JSON.parse(localStorage.getItem('products')) || [];

document.getElementById('product-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const title = document.getElementById('product-title').value;
    const mrp = document.getElementById('product-mrp').value;
    const price = document.getElementById('product-price').value;
    const image = document.getElementById('product-image').files[0];

    const reader = new FileReader();
    reader.onloadend = function() {
        const product = {
            id: Date.now(),
            title,
            mrp,
            price,
            imageUrl: reader.result
        };

        products.push(product);
        localStorage.setItem('products', JSON.stringify(products));

        alert('Product uploaded successfully!');
        window.location.href = 'shop.html';
    };

    if (image) {
        reader.readAsDataURL(image);
    } else {
        alert('Please select an image.');
    }
});
