import { formatMessageForDisplay } from './message_formatters.js';

export function initMessageDisplay(messagesDiv, eventFilterContainer, selectedEventsDiv, eventOptionsDiv, clearEventFilterButton, clearMessagesButton, ws) {
    let allMessages = [];
    const uniqueEvents = new Set();
    let selectedEvents = new Set();

    function updateSelectedEventsDisplay() {
        selectedEventsDiv.innerHTML = '';
        if (selectedEvents.size === 0) {
            selectedEventsDiv.innerHTML = '<span class="text-gray-500 px-1">选择事件...</span>';
        } else {
            selectedEvents.forEach(event => {
                const tag = document.createElement('span');
                tag.className = 'bg-gray-200 px-2 py-1 rounded-sm flex items-center gap-1';
                tag.textContent = event;
                const removeBtn = document.createElement('span');
                removeBtn.className = 'cursor-pointer font-bold text-gray-600 hover:text-black';
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
            option.className = 'px-2 py-1 cursor-pointer hover:bg-gray-100';
            option.textContent = event;
            option.dataset.event = event;
            if (selectedEvents.has(event)) {
                option.classList.add('bg-blue-50', 'font-bold');
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

    function filterAndDisplayMessages() {
        messagesDiv.innerHTML = '';
        allMessages.forEach(message => {
            if (selectedEvents.size === 0 || selectedEvents.has(message.tag)) {
                const messageContainer = document.createElement('div');
                messageContainer.className = 'flex items-start my-1 p-1 bg-gray-200 rounded-sm font-mono text-sm';
                messageContainer.dataset.event = message.tag;

                const eventTag = document.createElement('span');
                eventTag.className = 'bg-blue-500 text-white px-2 py-1 rounded-sm mr-2 min-w-[80px] text-center flex-shrink-0';
                eventTag.textContent = message.tag;
                messageContainer.appendChild(eventTag);

                const messageContentWrapper = document.createElement('div');
                messageContentWrapper.className = 'flex-grow flex-wrap items-center';

                const compactContent = document.createElement('span');
                compactContent.className = 'flex-grow whitespace-nowrap overflow-hidden text-ellipsis mr-1';
                compactContent.textContent = message.compactContent;
                messageContentWrapper.appendChild(compactContent);

                const toggleButton = document.createElement('button');
                toggleButton.className = 'bg-transparent border-none text-blue-500 cursor-pointer text-base p-0 px-1 flex-shrink-0 hover:text-blue-600';
                toggleButton.textContent = '▼';
                toggleButton.onclick = () => {
                    if (fullContent.style.display === 'block') {
                        fullContent.style.display = 'none';
                        toggleButton.textContent = '▼';
                    } else {
                        fullContent.style.display = 'block';
                        toggleButton.textContent = '▲';
                    }
                };
                messageContentWrapper.appendChild(toggleButton);
                const fullContent = document.createElement('pre');
                fullContent.className = 'basis-full whitespace-pre-wrap break-all mt-1 p-1 bg-gray-50 rounded-sm hidden';
                fullContent.textContent = message.fullContent;
                messageContentWrapper.appendChild(fullContent);

                messageContainer.appendChild(messageContentWrapper);
                messagesDiv.appendChild(messageContainer);
            }
        });
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    // WebSocket Event Handlers
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

    // Control Buttons and Filters
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

    // Initializations
    updateEventFilterOptions();
    updateSelectedEventsDisplay();

    return {
        tagMessage,
        allMessages,
        filterAndDisplayMessages,
        uniqueEvents,
        updateEventFilterOptions
    };
}