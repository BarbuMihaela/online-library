function removeMember(userId) {
    if (!confirm("Are you sure you want to remove this member?")) return;

    fetch('/remove_member', {
        method: 'DELETE',
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ user_id: userId })
    })
    .then(response => {
        const msgDiv = document.getElementById("error_msg");
        if (response.ok) {
            return response.json().then(data => {
                msgDiv.className = "success-msg";
                msgDiv.innerText = data.message || "User removed successfully.";
                const userItem = document.getElementById(`user_id_${userId}`);
                if (userItem) userItem.remove();
            });
        } else {
            return response.json().then(data => {
                msgDiv.className = "error-msg";
                msgDiv.innerText = data.message || "Error removing user.";
            });
        }
    })
    .catch(error => {
        const msgDiv = document.getElementById("error_msg");
        msgDiv.className = "error-msg";
        msgDiv.innerText = "Network error: " + error.message;
    });
}
