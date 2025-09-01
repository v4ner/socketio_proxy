document.addEventListener('DOMContentLoaded', (event) => {
    // --- Existing Elements ---
    const messagesDiv = document.getElementById('messages');
    const eventFilterContainer = document.getElementById('event-filter-container');
    const selectedEventsDiv = document.getElementById('selected-events');
    const eventOptionsDiv = document.getElementById('event-options');
    const clearEventFilterButton = document.getElementById('clear-event-filter');
    const clearMessagesButton = document.getElementById('clear-messages');
    const restartSioButton = document.getElementById('restart-sio-button');
    const baseUrl = window.BASE_URL;

    // --- Tab and Builder Elements ---
    const tabLinks = document.querySelectorAll('.tab-link');
    const tabContents = document.querySelectorAll('.tab-content');
    const messageBuilderSelect = document.getElementById('message-builder-select');
    const builderFieldsDiv = document.getElementById('builder-fields');
    const sendBuilderMessageButton = document.getElementById('send-builder-message-button');
    const builderPreview = document.getElementById('builder-preview');

    // --- JSON Tab Elements ---
    const messageInput = document.getElementById('message-input');
    const sendMessageButton = document.getElementById('send-message-button');
    const formatMessageButton = document.getElementById('format-message-button');

    // --- State Variables ---
    let allMessages = [];
    const uniqueEvents = new Set();
    let selectedEvents = new Set();

    // =================================================================
    // NEW LOGIC: Tab Switching
    // =================================================================
    tabLinks.forEach(link => {
        link.addEventListener('click', () => {
            const tabId = link.getAttribute('data-tab');

            tabLinks.forEach(innerLink => innerLink.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            link.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // =================================================================
    // Generic Send Function
    // =================================================================
    function sendMessage(messageObject) {
        console.log('Sending message:', messageObject);

        fetch(`${baseUrl}/send_message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(messageObject),
        })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log('Message sent successfully:', data);
            let sentMessage = { event: messageObject.event || 'sent', data: messageObject.data || messageObject };
            sentMessage = tagMessage(sentMessage);
            const formattedMessage = formatMessageForDisplay(sentMessage);
            allMessages.push({ ...sentMessage, ...formattedMessage });
            filterAndDisplayMessages();
        })
        .catch(error => {
            console.error('Error sending message:', error);
            alert(`发送消息失败: ${error.message}`);
        });
    }

    // =================================================================
    // EXISTING LOGIC (Adapted)
    // =================================================================

    // --- Original JSON sending logic ---
    function sendJsonMessage() {
        const messageText = messageInput.value;
        if (!messageText.trim()) {
            alert('消息内容不能为空！');
            return;
        }
        try {
            const parsedMessage = JSON.parse(messageText);
            sendMessage(parsedMessage);
            messageInput.value = ''; // Clear input after sending
        } catch (e) {
            alert('无效的JSON格式。请检查您的消息。');
            console.error('消息发送错误:', e);
        }
    }

    sendMessageButton.addEventListener('click', sendJsonMessage);
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendJsonMessage();
        }
    });

    formatMessageButton.addEventListener('click', () => {
        const messageText = messageInput.value;
        if (!messageText.trim()) return;
        try {
            const parsed = JSON.parse(messageText);
            messageInput.value = JSON.stringify(parsed, null, 2);
        } catch (e) {
            alert('无效的JSON格式，无法格式化。');
        }
    });

    // --- Message Display and Filtering (largely unchanged) ---
    function updateSelectedEventsDisplay() {
        selectedEventsDiv.innerHTML = '';
        if (selectedEvents.size === 0) {
            selectedEventsDiv.innerHTML = '<span class="placeholder">选择事件...</span>';
        } else {
            selectedEvents.forEach(event => {
                const tag = document.createElement('span');
                tag.className = 'event-tag';
                tag.textContent = event;
                const removeBtn = document.createElement('span');
                removeBtn.className = 'remove-tag';
                removeBtn.textContent = 'x';
                removeBtn.onclick = (e) => {
                    e.stopPropagation();
                    selectedEvents.delete(event);
                    updateSelectedEventsDisplay();
                    filterAndDisplayMessages();
                };
                tag.appendChild(removeBtn);
                selectedEventsDiv.appendChild(tag);
            });
        }
    }

    function updateEventFilterOptions() {
        eventOptionsDiv.innerHTML = '';
        uniqueEvents.forEach(event => {
            const option = document.createElement('div');
            option.className = 'event-option';
            option.textContent = event;
            option.dataset.event = event;
            if (selectedEvents.has(event)) {
                option.classList.add('selected');
            }
            option.onclick = () => {
                selectedEvents.has(event) ? selectedEvents.delete(event) : selectedEvents.add(event);
                updateSelectedEventsDisplay();
                filterAndDisplayMessages();
                option.classList.toggle('selected');
            };
            eventOptionsDiv.appendChild(option);
        });
    }

    function tagMessage(message) {
        message.tag = message.event || 'unknown';
        return message;
    }

    // The formatMessageForDisplay function is now defined in message_formatters.js

    function filterAndDisplayMessages() {
        messagesDiv.innerHTML = '';
        allMessages.forEach(message => {
            if (selectedEvents.size === 0 || selectedEvents.has(message.tag)) {
                const messageContainer = document.createElement('div');
                messageContainer.className = 'message-item';
                messageContainer.dataset.event = message.tag;

                const eventTag = document.createElement('span');
                eventTag.className = 'message-event-tag';
                eventTag.textContent = message.tag;
                messageContainer.appendChild(eventTag);

                const messageContentWrapper = document.createElement('div');
                messageContentWrapper.className = 'message-content-wrapper';

                const compactContent = document.createElement('span');
                compactContent.className = 'message-compact-content';
                compactContent.textContent = message.compactContent;
                messageContentWrapper.appendChild(compactContent);

                const toggleButton = document.createElement('button');
                toggleButton.className = 'message-toggle-button';
                toggleButton.textContent = '▼';
                toggleButton.onclick = () => {
                    fullContent.classList.toggle('show');
                    toggleButton.textContent = fullContent.classList.contains('show') ? '▲' : '▼';
                };
                messageContentWrapper.appendChild(toggleButton);

                const fullContent = document.createElement('pre');
                fullContent.className = 'message-full-content';
                fullContent.textContent = message.fullContent;
                messageContentWrapper.appendChild(fullContent);

                messageContainer.appendChild(messageContentWrapper);
                messagesDiv.appendChild(messageContainer);
            }
        });
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    // --- WebSocket Logic (unchanged) ---
    const ws = new WebSocket(`ws://${window.location.host}${baseUrl}/ws`);

    ws.onopen = (event) => {
        console.log('WebSocket connected:', event);
        let msg = tagMessage({ type: 'status', content: 'WebSocket connected!' });
        const formattedMsg = formatMessageForDisplay(msg);
        allMessages.push({ ...msg, ...formattedMsg });
        filterAndDisplayMessages();
    };

    ws.onmessage = (event) => {
        try {
            let message = JSON.parse(event.data);
            message = tagMessage(message);
            const formattedMessage = formatMessageForDisplay(message);

            if (!uniqueEvents.has(message.tag)) {
                uniqueEvents.add(message.tag);
                updateEventFilterOptions();
            }
            allMessages.push({ ...message, ...formattedMessage });
            filterAndDisplayMessages();
        } catch (e) {
            let msg = tagMessage({ type: 'error', content: `Received non-JSON message: ${event.data}` });
            const formattedMsg = formatMessageForDisplay(msg);
            allMessages.push({ ...msg, ...formattedMsg });
            filterAndDisplayMessages();
        }
    };

    ws.onclose = (event) => {
        let msg = tagMessage({ type: 'status', content: 'WebSocket disconnected!' });
        const formattedMsg = formatMessageForDisplay(msg);
        allMessages.push({ ...msg, ...formattedMsg });
        filterAndDisplayMessages();
    };

    ws.onerror = (error) => {
        let msg = tagMessage({ type: 'error', content: `WebSocket error: ${error.message}` });
        const formattedMsg = formatMessageForDisplay(msg);
        allMessages.push({ ...msg, ...formattedMsg });
        filterAndDisplayMessages();
    };

    // --- Control Buttons and Filters (unchanged) ---
    eventFilterContainer.addEventListener('click', () => {
        eventOptionsDiv.classList.toggle('show');
    });

    document.addEventListener('click', (e) => {
        if (!eventFilterContainer.contains(e.target) && eventOptionsDiv.classList.contains('show')) {
            eventOptionsDiv.classList.remove('show');
        }
    });

    clearEventFilterButton.addEventListener('click', () => {
        selectedEvents.clear();
        updateSelectedEventsDisplay();
        updateEventFilterOptions();
        filterAndDisplayMessages();
    });

    clearMessagesButton.addEventListener('click', () => {
        allMessages = [];
        uniqueEvents.clear();
        selectedEvents.clear();
        messagesDiv.innerHTML = '';
        updateEventFilterOptions();
        updateSelectedEventsDisplay();
    });

    restartSioButton.addEventListener('click', () => {
        if (confirm('确定要重启Socket.IO连接吗？')) {
            fetch(`${baseUrl}/restart_sio`, { method: 'POST' })
            .then(response => {
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                return response.json();
            })
            .then(data => {
                alert('Socket.IO连接重启成功！');
                console.log('Restart SIO successful:', data);
            })
            .catch(error => {
                alert(`Socket.IO连接重启失败: ${error.message}`);
                console.error('Error restarting SIO:', error);
            });
        }
    });

    // --- Initializations ---
    updateEventFilterOptions();
    updateSelectedEventsDisplay();

    // Initialize the message builder UI
    initMessageBuilder(
        messageBuilderSelect,
        builderFieldsDiv,
        sendBuilderMessageButton,
        builderPreview,
        sendMessage
    );
});