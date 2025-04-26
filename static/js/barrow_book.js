 function barrowBook(bookId) {
        if (!confirm("Are you sure you want to barrow this book?")) return;
        fetch(('/barrow_book'), { method: 'POST' ,
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ book_id : bookId}) })
            .then(response => {
                if (response.ok) {
                    alert("in cos.");
                    document.getElementById('book_id_${bookId}').remove();
                } else {
                    alert("Error barrow this book.");
                }
            });
    }
