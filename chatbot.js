// chatbot.js
document.addEventListener('DOMContentLoaded', (event) => {
    // Lógica para abrir/fechar o pop-up
    const bubble = document.getElementById('climabot-bubble');
    const popup = document.getElementById('climabot-popup');
    const closeBtn = document.querySelector('#climabot-popup .close-btn');
    
    if (bubble && popup && closeBtn) {
        function togglePopup() { 
            popup.classList.toggle('active'); 
        }
        bubble.addEventListener('click', togglePopup);
        closeBtn.addEventListener('click', togglePopup);
    }

    // Lógica do Chat
    const messagesContainer = document.getElementById('climabot-messages');
    const input = document.getElementById('climabot-input');
    const sendBtn = document.getElementById('climabot-send-btn');

    // URL da nossa API na Netlify
    const API_URL = 'https://climabot-api.onrender.com/api';

    async function sendMessage() {
        if (!input || !messagesContainer) return;
        const pergunta = input.value.trim();
        if (!pergunta) return;

        addMessage(pergunta, 'user');
        input.value = '';
        addMessage('...', 'assistant', true);

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pergunta: pergunta })
            });
            const data = await response.json();
            updateLastMessage(data.resposta || 'Desculpe, ocorreu um erro.');
        } catch (error) {
            updateLastMessage('Não consigo responder agora. Tente mais tarde.');
        }
    }

    function addMessage(text, role, isLoading = false) {
        if (!messagesContainer) return;
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${role}-message`;
        messageDiv.textContent = text;
        if (isLoading) messageDiv.id = 'loading-indicator';
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function updateLastMessage(text) {
        const loadingIndicator = document.getElementById('loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.textContent = text;
            loadingIndicator.id = '';
        }
    }

    if (sendBtn && input) {
        sendBtn.addEventListener('click', sendMessage);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    }
});
