let products = [
    { id: 1, name: 'Producto 1', price: 10.00 },
    { id: 2, name: 'Producto 2', price: 15.00 },
    { id: 3, name: 'Producto 3', price: 20.00 }
];

let saleItems = [];

function addProduct() {
    let searchValue = document.getElementById('product-search').value.toLowerCase();
    let product = products.find(p => p.name.toLowerCase().includes(searchValue));

    if (product) {
        let saleItem = saleItems.find(item => item.product.id === product.id);
        if (saleItem) {
            saleItem.quantity++;
        } else {
            saleItems.push({ product, quantity: 1 });
        }
        renderSaleItems();
    } else {
        alert('Producto no encontrado');
    }
}

function renderSaleItems() {
    let salesBody = document.getElementById('sales-body');
    salesBody.innerHTML = '';

    saleItems.forEach((item, index) => {
        let row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.product.name}</td>
            <td>${item.product.price.toFixed(2)}</td>
            <td>${item.quantity}</td>
            <td>${(item.product.price * item.quantity).toFixed(2)}</td>
            <td><button onclick="removeItem(${index})">Eliminar</button></td>
        `;
        salesBody.appendChild(row);
    });

    updateTotal();
}

function removeItem(index) {
    saleItems.splice(index, 1);
    renderSaleItems();
}

function updateTotal() {
    let total = saleItems.reduce((acc, item) => acc + (item.product.price * item.quantity), 0);
    document.getElementById('total-venta').innerText = total.toFixed(2);
    updateChange();
}

function updateChange() {
    let total = parseFloat(document.getElementById('total-venta').innerText);
    let pago = parseFloat(document.getElementById('pago').value) || 0;
    let cambio = pago - total;
    document.getElementById('cambio').innerText = cambio.toFixed(2);
}

document.getElementById('pago').addEventListener('input', updateChange);

function guardarTicket() {
    let ticketContent = `
        <h1>Ticket de Venta</h1>
        <table>
            <thead>
                <tr>
                    <th>Producto</th>
                    <th>Precio</th>
                    <th>Cantidad</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
                ${saleItems.map(item => `
                    <tr>
                        <td>${item.product.name}</td>
                        <td>${item.product.price.toFixed(2)}</td>
                        <td>${item.quantity}</td>
                        <td>${(item.product.price * item.quantity).toFixed(2)}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
        <p>Total de la venta: ${document.getElementById('total-venta').innerText}</p>
        <p>Pago: ${document.getElementById('pago').value}</p>
        <p>Cambio: ${document.getElementById('cambio').innerText}</p>
    `;

    let newWindow = window.open('', '', 'width=800,height=600');
    newWindow.document.write(ticketContent);
    newWindow.document.close();
    newWindow.print();
}
