 function borrowBook(bookId) {
    if (!confirm("Are you sure you want to borrow this book?")) return;

    fetch('/borrow_book', {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ book_id: bookId })
    })
    .then(response => {
        if (response.ok) {
            alert("The book has been successfully added to your cart.");
            const bookRow = document.getElementById(`book_id_${bookId}`);
            if (bookRow) bookRow.remove();  // elimină elementul din DOM
        } else {
            return response.json().then(data => {
                alert(data.message || "Error borrowing this book.");
            });
        }
    })
    .catch(error => {
        alert("Network error: " + error.message);
    });
}
