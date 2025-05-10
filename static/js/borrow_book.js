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
        const contentType = response.headers.get("content-type") || "";
        if (!contentType.includes("application/json")) {
            throw new Error("Server did not return JSON");
        }
        return response.json();
    })
    .then(data => {
        if (data.status === "success") {
            alert(data.message);
            window.location.href = "/user_view_books";
            const bookRow = document.getElementById(`book_id_${bookId}`);
            if (bookRow) bookRow.remove();
        } else {
            alert(data.message || "Error borrowing this book.");
        }
    })
    .catch(error => {
        alert("Network error: " + error.message);
    });
}
