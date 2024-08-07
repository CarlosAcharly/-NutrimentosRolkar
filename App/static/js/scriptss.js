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
