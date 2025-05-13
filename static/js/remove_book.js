function removeBook(bookId) {
    if (!confirm("Are you sure you want to remove this book?")) return;

    fetch('/remove_book', {
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
        if (data.success) {
            alert(data.message);
            const bookRow = document.getElementById(`book-${bookId}`);
            if (bookRow) {
                bookRow.remove();
            }

            setTimeout(() => {
                window.location.href = "/view_books";
            }, 800);
        } else {
            alert(data.message || "Error removing this book.");
        }
    })
    .catch(error => {
        alert("Network error: " + error.message);
    });
}
