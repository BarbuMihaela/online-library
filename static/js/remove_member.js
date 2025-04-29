function removeMember(userId) {
        if (!confirm("Are you sure you want to remove this member?")) return;
        fetch(('/remove_member'), {
            method: 'DELETE' ,
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ user_id: userId}) });

           alert("user has been removed succesfully");
    }

