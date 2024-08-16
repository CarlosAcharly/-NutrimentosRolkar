document.addEventListener('DOMContentLoaded', function () {
    const tableBody = document.getElementById('table-body');
    const totalValue = document.getElementById('total-value');

    function calculateTotal() {
        let total = 0;
        const importes = tableBody.querySelectorAll('.importe');
        importes.forEach(function (importe) {
            total += parseFloat(importe.textContent);
        });
        totalValue.textContent = total.toFixed(2);
    }

    tableBody.addEventListener('click', function (event) {
        if (event.target.classList.contains('delete-row')) {
            const row = event.target.closest('tr');
            row.remove();
            calculateTotal();
        }
    });

    calculateTotal();
    document.getElementById('calculate-change').addEventListener('click', function() {
        const totalValue = parseFloat(document.getElementById('total-value').textContent);
        const paymentAmount = parseFloat(document.getElementById('payment-amount').value);
        const changeValue = paymentAmount - totalValue;
        document.getElementById('change-value').textContent = changeValue.toFixed(2);
    });
    
    function numberToWords(num) {
        const ones = ['cero', 'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve'];
        const tens = ['', '', 'veinte', 'treinta', 'cuarenta', 'cincuenta', 'sesenta', 'setenta', 'ochenta', 'noventa'];
        const teens = ['diez', 'once', 'doce', 'trece', 'catorce', 'quince', 'dieciséis', 'diecisiete', 'dieciocho', 'diecinueve'];
    
        if (num < 10) return ones[num];
        if (num < 20) return teens[num - 10];
        if (num < 100) {
            return tens[Math.floor(num / 10)] + (num % 10 !== 0 ? ' y ' + ones[num % 10] : '');
        }
        if (num < 1000) {
            return ones[Math.floor(num / 100)] + 'cientos' + (num % 100 !== 0 ? ' ' + numberToWords(num % 100) : '');
        }
        return '';
    }
    
    function updateTotalInWords() {
        const totalValue = parseFloat(document.getElementById('total-value').textContent);
        const totalInWords = numberToWords(Math.floor(totalValue));
        document.getElementById('total-in-words').textContent = totalInWords + ' pesos';
    }
    
    updateTotalInWords();
    document.getElementById('user-dropdown').addEventListener('click', function() {
        document.getElementById('dropdown-menu').classList.toggle('show');
    });
    
    window.onclick = function(event) {
        if (!event.target.matches('.dropdown')) {
            var dropdowns = document.getElementsByClassName("dropdown-content");
            for (var i = 0; i < dropdowns.length; i++) {
                var openDropdown = dropdowns[i];
                if (openDropdown.classList.contains('show')) {
                    openDropdown.classList.remove('show');
                }
            }
        }
    };
    document.getElementById("cancel").addEventListener("click", function() {
        window.location.href = "dashboardProductos.html";
    });
    
    document.getElementById('logout').addEventListener('click', function() {
        // Lógica para cerrar sesión
        alert('Cerrar sesión');
    });
    
    document.getElementById('help').addEventListener('click', function() {
        // Lógica para mostrar ayuda
        alert('Ayuda');
    });    
});
// Simulación de una lista de productos. En un entorno real, esto vendría de una API.
const productos = [
    { id: 1, nombre: 'Maiz', marca: 'Molido', precio: 250 },
    { id: 2, nombre: 'Lechero', marca: 'Nogal', precio: 320 },
    // Agregar más productos aquí
];

function searchProduct() {
    const query = document.getElementById('product-search').value.toLowerCase();
    const filteredProducts = productos.filter(producto => {
        return producto.nombre.toLowerCase().includes(query) ||
               producto.marca.toLowerCase().includes(query) ||
               producto.precio.toString().includes(query);
    });

    const productsList = document.getElementById('products-list');
    productsList.innerHTML = ''; // Limpiar la lista anterior
    filteredProducts.forEach(producto => {
        productsList.innerHTML += `
            <tr>
                <td>${producto.nombre}</td>
                <td>${producto.marca}</td>
                <td>${producto.precio}</td>
                <td><button onclick="addToCart(${producto.id})">Agregar</button></td>
            </tr>
        `;
    });
}

document.getElementById('product-search').addEventListener('input', searchProduct);
let carrito = [];

function addToCart(productId) {
    const producto = productos.find(p => p.id === productId);
    if (producto) {
        carrito.push(producto);
        updateSalesTable();
    }
}

function updateSalesTable() {
    const salesBody = document.getElementById('sales-body');
    salesBody.innerHTML = ''; // Limpiar la tabla de ventas
    let totalVenta = 0;
    carrito.forEach((producto, index) => {
        totalVenta += producto.precio;
        salesBody.innerHTML += `
            <tr>
                <td>${producto.nombre}</td>
                <td>${producto.marca}</td>
                <td>${producto.precio}</td>
                <td><button onclick="removeFromCart(${index})">Eliminar</button></td>
            </tr>
        `;
    });
    document.getElementById('total-venta').innerText = totalVenta.toFixed(2);
}

function removeFromCart(index) {
    carrito.splice(index, 1);
    updateSalesTable();
}
function guardarTicket() {
    // Aquí enviarías los datos al servidor usando AJAX o Fetch API
    fetch('/cajero/ventas', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ carrito: carrito })
    }).then(response => {
        if (response.ok) {
            alert('Venta guardada e imprimida con éxito');
            carrito = [];
            updateSalesTable();
        } else {
            alert('Hubo un error al guardar la venta');
        }
    });
}
