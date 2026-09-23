/**
 * Furnish Agentic AI Assistant
 * Powered by Google AI Studio API (Gemini)
 */

document.addEventListener('DOMContentLoaded', function () {
    const aiWidget = document.getElementById('furnish-ai-widget');
    if (!aiWidget) return;

    const launcherBtn = document.getElementById('furnish-ai-launcher');
    const closeBtn = document.getElementById('furnish-ai-close');
    const minimizeBtn = document.getElementById('furnish-ai-minimize');
    const clearBtn = document.getElementById('furnish-ai-clear');
    const chatContainer = document.getElementById('furnish-ai-chat-window');
    const messagesContainer = document.getElementById('furnish-ai-messages');
    const chatInput = document.getElementById('furnish-ai-input');
    const sendBtn = document.getElementById('furnish-ai-send-btn');
    const suggestionPills = document.querySelectorAll('.ai-suggestion-pill');

    // Get CSRF Token
    function getCsrfToken() {
        const csrfCookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
        if (csrfCookie) {
            return csrfCookie.split('=')[1];
        }
        const inputElem = document.querySelector('[name=csrfmiddlewaretoken]');
        return inputElem ? inputElem.value : '';
    }

    // Toggle Chat Window
    function openChat() {
        chatContainer.classList.add('active');
        launcherBtn.classList.add('hide');
        chatInput.focus();
        scrollToBottom();
    }

    function closeChat() {
        chatContainer.classList.remove('active');
        launcherBtn.classList.remove('hide');
    }

    if (launcherBtn) launcherBtn.addEventListener('click', openChat);
    if (closeBtn) closeBtn.addEventListener('click', closeChat);
    if (minimizeBtn) minimizeBtn.addEventListener('click', closeChat);

    // Escape key closes widget
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && chatContainer.classList.contains('active')) {
            closeChat();
        }
    });

    // Scroll to bottom of chat
    function scrollToBottom() {
        setTimeout(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 50);
    }

    // Simple markdown to HTML parser
    function formatMarkdown(text) {
        if (!text) return '';
        let html = text
            // Escape HTML characters
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            // Blockquotes
            .replace(/^>\s*(.+)$/gm, '<blockquote class="ai-quote">$1</blockquote>')
            // Bold
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Italic
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Links [text](url)
            .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" class="ai-chat-link">$1</a>')
            // Bullet points
            .replace(/^\s*-\s+(.+)$/gm, '<li>$1</li>');

        // Wrap consecutive <li> into <ul>
        html = html.replace(/(<li>.*?<\/li>)+/gs, '<ul class="ai-chat-list mb-2">$&</ul>');

        // Line breaks
        html = html.replace(/\n\n/g, '<br><br>').replace(/\n/g, '<br>');
        return html;
    }

    // Append Message to UI
    function appendMessage(sender, text, products = [], cartAction = null) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `ai-message-row ${sender === 'user' ? 'user-message-row' : 'bot-message-row'}`;

        const isBot = sender !== 'user';
        const formattedText = formatMarkdown(text);

        let contentHtml = `
            <div class="ai-message-bubble ${isBot ? 'ai-bot-bubble' : 'ai-user-bubble'}">
                <div class="ai-message-text">${formattedText}</div>
        `;

        // Render Cart Action Notification if any
        if (cartAction && cartAction.action === 'added') {
            contentHtml += `
                <div class="ai-cart-banner mt-2 p-2 rounded-3 d-flex align-items-center justify-content-between">
                    <span class="small"><i class="bi bi-check-circle-fill text-success me-1"></i> Added to your Cart</span>
                    <a href="/cart/" class="btn btn-sm btn-dark py-0 px-2 text-xs">View Cart</a>
                </div>
            `;
        }

        // Render Rich Product Cards if returned
        if (products && products.length > 0) {
            contentHtml += `
                <div class="ai-products-deck mt-3">
                    <div class="ai-products-carousel">
            `;
            products.forEach(prod => {
                const img = prod.image_url || '/static/assets/images/placeholder.jpg';
                const formattedPrice = Number(prod.price).toLocaleString('en-IN');
                contentHtml += `
                    <div class="ai-product-card">
                        <div class="ai-product-thumb">
                            <img src="${img}" alt="${prod.name}" onerror="this.src='/static/assets/images/placeholder.jpg';" />
                            <span class="ai-product-badge">${prod.category}</span>
                        </div>
                        <div class="ai-product-info">
                            <h6 class="ai-product-title" title="${prod.name}">${prod.name}</h6>
                            <div class="ai-product-price">₹${formattedPrice}</div>
                            <div class="ai-product-actions">
                                <a href="/product/${prod.slug}" class="btn btn-outline-dark btn-sm ai-btn-view">View</a>
                                <button type="button" class="btn btn-dark btn-sm ai-btn-add" data-pid="${prod.id}" data-name="${prod.name}">
                                    <i class="bi bi-cart-plus"></i> Add
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            });
            contentHtml += `
                    </div>
                </div>
            `;
        }

        contentHtml += `
                <div class="ai-message-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
            </div>
        `;

        msgDiv.innerHTML = contentHtml;
        messagesContainer.appendChild(msgDiv);
        scrollToBottom();

        // Attach 1-click Add-to-Cart handlers on newly rendered cards
        const addButtons = msgDiv.querySelectorAll('.ai-btn-add');
        addButtons.forEach(btn => {
            btn.addEventListener('click', function () {
                const pid = this.getAttribute('data-pid');
                const name = this.getAttribute('data-name');
                handleDirectAddToCart(pid, name, this);
            });
        });
    }

    // Append Typing Indicator
    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'ai-typing-indicator';
        indicator.className = 'ai-message-row bot-message-row';
        indicator.innerHTML = `
            <div class="ai-message-bubble ai-bot-bubble ai-typing-bubble">
                <span class="ai-typing-label">Furnish AI thinking</span>
                <span class="ai-dot"></span>
                <span class="ai-dot"></span>
                <span class="ai-dot"></span>
            </div>
        `;
        messagesContainer.appendChild(indicator);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('ai-typing-indicator');
        if (indicator) indicator.remove();
    }

    // Direct 1-Click Add-to-Cart handler inside chat
    function handleDirectAddToCart(productId, productName, buttonElem) {
        buttonElem.disabled = true;
        buttonElem.innerHTML = `<span class="spinner-border spinner-border-sm" role="status"></span>`;

        fetch(`/add-to-cart/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `quantity=1`
        })
        .then(response => {
            buttonElem.innerHTML = `<i class="bi bi-check-lg text-success"></i> Added`;
            buttonElem.classList.remove('btn-dark');
            buttonElem.classList.add('btn-outline-success');
            // Update cart badges
            fetchCartCount();
        })
        .catch(err => {
            console.error('Cart add error:', err);
            buttonElem.disabled = false;
            buttonElem.innerHTML = `<i class="bi bi-cart-plus"></i> Add`;
        });
    }

    // Update cart counts everywhere on page
    function updateCartBadges(count) {
        if (count === undefined || count === null) return;
        const badges = document.querySelectorAll('.badge.bg-dark.rounded-pill, .cart-count-badge');
        badges.forEach(b => {
            b.textContent = count;
        });
    }

    function fetchCartCount() {
        // Can re-check cart via AI endpoint or let user know
        sendMessageSilent('What is my cart count?');
    }

    function sendMessageSilent(query) {
        fetch('/ai/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ message: query })
        })
        .then(res => res.json())
        .then(data => {
            if (data.cart_count !== undefined) {
                updateCartBadges(data.cart_count);
            }
        })
        .catch(() => {});
    }

    // Send User Message
    function sendMessage(text) {
        const messageText = (text || chatInput.value).trim();
        if (!messageText) return;

        appendMessage('user', messageText);
        chatInput.value = '';
        showTypingIndicator();

        fetch('/ai/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({ message: messageText })
        })
        .then(res => {
            if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
            return res.json();
        })
        .then(data => {
            removeTypingIndicator();
            if (data.status === 'success') {
                appendMessage('bot', data.message, data.products, data.cart_action);
                if (data.cart_count !== undefined) {
                    updateCartBadges(data.cart_count);
                }
            } else {
                appendMessage('bot', data.message || "I encountered a momentary issue. Please try again.");
            }
        })
        .catch(err => {
            removeTypingIndicator();
            console.error('AI chat error:', err);
            appendMessage('bot', "Sorry, I am having trouble connecting right now. Please verify your connection or Google AI Studio API key.");
        });
    }

    // Input Events
    if (sendBtn) {
        sendBtn.addEventListener('click', () => sendMessage());
    }

    if (chatInput) {
        chatInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    // Suggestion pills click
    suggestionPills.forEach(pill => {
        pill.addEventListener('click', function () {
            const query = this.getAttribute('data-query') || this.textContent.trim();
            openChat();
            sendMessage(query);
        });
    });

    // Clear History Button
    if (clearBtn) {
        clearBtn.addEventListener('click', function () {
            if (!confirm('Clear your AI conversation history?')) return;
            fetch('/ai/clear/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            })
            .then(res => res.json())
            .then(() => {
                messagesContainer.innerHTML = `
                    <div class="ai-message-row bot-message-row">
                        <div class="ai-message-bubble ai-bot-bubble">
                            <div class="ai-message-text">
                                Hello! I'm your <strong>Furnish AI Concierge</strong>. How can I help you furnish your dream space today?
                            </div>
                            <div class="ai-message-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                        </div>
                    </div>
                `;
            });
        });
    }
});
