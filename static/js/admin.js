document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.search-box input');
    const usersContainer = document.getElementById('activeUsers');
    const messageArea = document.getElementById('messageArea');
    const chatInput = document.querySelector('.chat-input textarea');
    const sendButton = document.querySelector('.send-btn');
    let currentPhoneNumber = null;

    // Search users
    searchInput.addEventListener('input', debounce(searchUsers, 300));

    // Quick reply buttons
    document.querySelectorAll('.quick-reply').forEach(button => {
        button.addEventListener('click', () => {
            if (currentPhoneNumber) {
                sendMessage(currentPhoneNumber, button.textContent);
            }
        });
    });

    // Send message
    sendButton.addEventListener('click', () => {
        if (currentPhoneNumber && chatInput.value.trim()) {
            sendMessage(currentPhoneNumber, chatInput.value.trim());
            chatInput.value = '';
        }
    });

    async function searchUsers(event) {
        const query = event.target.value;
        try {
            const response = await fetch(`/api/users/search?q=${query}`);
            const users = await response.json();
            displayUsers(users);
        } catch (error) {
            console.error('Error searching users:', error);
        }
    }

    async function sendMessage(phoneNumber, message) {
        try {
            const response = await fetch('/api/send-reply', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ phone_number: phoneNumber, message })
            });
            const result = await response.json();
            if (result.success) {
                appendMessage(message, 'outgoing');
            }
        } catch (error) {
            console.error('Error sending message:', error);
        }
    }

    function displayUsers(users) {
        usersContainer.innerHTML = users.map(user => `
            <div class="user-item" data-phone="${user.phone_number}">
                <div class="user-name">${user.name || 'Unknown'}</div>
                <div class="user-phone">${user.phone_number}</div>
            </div>
        `).join('');
    }

    function appendMessage(message, direction) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${direction}`;
        messageDiv.textContent = message;
        messageArea.appendChild(messageDiv);
        messageArea.scrollTop = messageArea.scrollHeight;
    }

    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }
});
