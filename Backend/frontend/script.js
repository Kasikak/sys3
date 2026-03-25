// Load items into table on page load
async function loadItems() {
    const res = await fetch('/get-items');
    const items = await res.json();

    const tbody = document.getElementById('itemTableBody');
    tbody.innerHTML = '';

    items.forEach(item => {
        tbody.innerHTML += `
            <tr>
                <td>${item.ItemName}</td>
                <td>${item.Quantity}</td>
                <td>${item.Price}</td>
                <td>${item.Stock}</td>
            </tr>
        `;
    });
}

function showMessage(text) {
    document.getElementById('message').textContent = text;
}

async function addItem() {
    const payload = {
        ItemName: document.getElementById('itemName').value,
        Quantity: parseInt(document.getElementById('quantity').value),
        Price:    parseFloat(document.getElementById('price').value),
        Stock:    parseInt(document.getElementById('stock').value)
    };

    const res = await fetch('/add-item', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    const data = await res.json();
    showMessage(data.message || data.error);
    loadItems();  // refresh table
}

async function removeItem() {
    const payload = {
        ItemName: document.getElementById('itemName').value
    };

    const res = await fetch('/remove-item', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    const data = await res.json();
    showMessage(data.message || data.error);
    loadItems();
}

async function updateItem() {
    const payload = {
        ItemName: document.getElementById('itemName').value,
        Quantity: parseInt(document.getElementById('quantity').value),
        Price:    parseFloat(document.getElementById('price').value),
        Stock:    parseInt(document.getElementById('stock').value)
    };

    const res = await fetch('/update-item', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    const data = await res.json();
    showMessage(data.message || data.error);
    loadItems();
}

// Load on page start
loadItems();