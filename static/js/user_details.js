document.addEventListener('DOMContentLoaded', function() {
    // Get messages every 5 seconds
    setInterval(fetchMessages, 5000);

    function fetchMessages() {
        fetch('/messages')
            .then(response => response.json())
            .then(messages => {
                if (messages.error) {
                    console.error('Error fetching messages:', messages.error);
                    return;
                }
                updateMessagesDisplay(messages);
            })
            .catch(error => console.error('Error:', error));
    }

    function updateMessagesDisplay(messages) {
        const container = document.getElementById('messages');
        if (!messages.length) return;
        
        messages.forEach(msg => {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${msg.category || 'info'}`;
            alertDiv.textContent = msg.message;
            container.appendChild(alertDiv);
        });
    }
});
