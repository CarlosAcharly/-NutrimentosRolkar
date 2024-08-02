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
