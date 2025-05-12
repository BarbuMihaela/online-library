function removeBook(bookId) {
    if (!confirm("Are you sure you want to remove this book?")) return;

    fetch('/remove_book', {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ book_id: bookId })
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        } else {
            location.reload();
        }
    })
    .catch(error => {
        alert("Error removing book: " + error.message);
    });
}
