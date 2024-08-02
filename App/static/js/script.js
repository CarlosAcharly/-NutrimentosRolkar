document.addEventListener('DOMContentLoaded', () => {
    // Establecer la fecha y hora actuales al cargar la página
    const now = new Date();
    document.getElementById('fecha').value = now.toISOString().split('T')[0]; // Fecha en formato YYYY-MM-DD
    document.getElementById('hora').value = now.toTimeString().split(' ')[0].substring(0, 5); // Hora en formato HH:MM
});

let totalVentas = 0;
let totalGastos = 0;

function calcularVentas() {
    const billetes1000 = parseFloat(document.getElementById('billetes1000').value) || 0;
    const billetes500 = parseFloat(document.getElementById('billetes500').value) || 0;
    const billetes200 = parseFloat(document.getElementById('billetes200').value) || 0;
    const billetes100 = parseFloat(document.getElementById('billetes100').value) || 0;
    const billetes50 = parseFloat(document.getElementById('billetes50').value) || 0;
    const billetes20 = parseFloat(document.getElementById('billetes20').value) || 0;
    const monedas20 = parseFloat(document.getElementById('monedas20').value) || 0;
    const monedas10 = parseFloat(document.getElementById('monedas10').value) || 0;
    const monedas5 = parseFloat(document.getElementById('monedas5').value) || 0;
    const monedas2 = parseFloat(document.getElementById('monedas2').value) || 0;
    const monedas1 = parseFloat(document.getElementById('monedas1').value) || 0;
    const monedas050 = parseFloat(document.getElementById('monedas050').value) || 0;

    totalVentas = (billetes1000 * 1000) +
                  (billetes500 * 500) +
                  (billetes200 * 200) +
                  (billetes100 * 100) +
                  (billetes50 * 50) +
                  (billetes20 * 20) +
                  (monedas20 * 20) +
                  (monedas10 * 10) +
                  (monedas5 * 5) +
                  (monedas2 * 2) +
                  (monedas1 * 1) +
                  (monedas050 * 0.5);

    document.getElementById('totalVentas').textContent = `Total Ventas: $${totalVentas.toFixed(2)}`;
    actualizarSaldoNeto();
}

function agregarGasto() {
    const gasto = parseFloat(document.getElementById('gasto').value) || 0;
    totalGastos += gasto;
    document.getElementById('totalGastos').textContent = `Total Gastos: $${totalGastos.toFixed(2)}`;
    actualizarSaldoNeto();
}

function actualizarSaldoNeto() {
    const saldoNeto = totalVentas - totalGastos;
    document.getElementById('saldoNeto').textContent = `Saldo Neto: $${saldoNeto.toFixed(2)}`;
}

function guardarCorte() {
    // Función para guardar el corte de caja
    alert('Corte de caja guardado exitosamente!');
}

function imprimirCorte() {
    // Función para imprimir el corte de caja
    window.print();
}
let totalExpenses = 0;

function addExpense() {
    const expenseDescription = document.getElementById('expense-description').value;
    const expenseAmount = parseFloat(document.getElementById('expense-amount').value);
    const expenseType = document.getElementById('expense-type').value;

    if (expenseDescription && expenseAmount && expenseType) {
        const tableBody = document.querySelector('#expenses-table tbody');
        const newRow = document.createElement('tr');

        const descriptionCell = document.createElement('td');
        descriptionCell.textContent = expenseDescription;

        const amountCell = document.createElement('td');
        amountCell.textContent = `$${expenseAmount.toFixed(2)}`;

        const typeCell = document.createElement('td');
        typeCell.textContent = expenseType;

        newRow.appendChild(descriptionCell);
        newRow.appendChild(amountCell);
        newRow.appendChild(typeCell);
        tableBody.appendChild(newRow);

        totalExpenses += expenseAmount;
        document.getElementById('total-expenses').textContent = totalExpenses.toFixed(2);

        document.getElementById('expense-description').value = '';
        document.getElementById('expense-amount').value = '';
        document.getElementById('expense-type').value = '';
    } else {
        alert('Por favor, completa todos los campos.');
    }
}
