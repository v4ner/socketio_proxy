import { initMessageDisplay } from './message_display.js';
import { initJsonMessageSender } from './json_message_sender.js';
import { formatMessageForDisplay } from './message_formatters.js';
import { initMessageBuilder } from './message_builder_ui.js';

document.addEventListener('DOMContentLoaded', (event) => {
    // --- Existing Elements ---
    const restartSioButton = document.getElementById('restart-sio-button');
    const baseUrl = window.BASE_URL;

    // --- Tab and Builder Elements ---
    const tabLinks = document.querySelectorAll('.tab-link');
    const tabContents = document.querySelectorAll('.tab-content');
    const messageBuilderSelect = document.getElementById('message-builder-select');
    const builderFieldsDiv = document.getElementById('builder-fields');
    const sendBuilderMessageButton = document.getElementById('send-builder-message-button');
    const builderPreview = document.getElementById('builder-preview');

    // =================================================================
    // NEW LOGIC: Tab Switching
    // =================================================================
    tabLinks.forEach(link => {
        link.addEventListener('click', () => {
            const tabId = link.getAttribute('data-tab');

            tabLinks.forEach(innerLink => {
                // 移除激活状态的特定样式
                innerLink.classList.remove('active', 'bg-blue-500', 'border-blue-500', 'cursor-default', 'font-bold', 'text-white');
                // 添加非激活状态的特定样式
                innerLink.classList.add('bg-gray-400', 'border-gray-400', 'border-b', 'text-gray-800', 'hover:bg-gray-500');
            });

            tabContents.forEach(content => {
                content.classList.remove('flex', 'flex-col');
                content.classList.add('hidden');
            });

            // 移除非激活状态的特定样式
            link.classList.remove('bg-gray-400', 'border-gray-400', 'border-b', 'text-gray-800', 'hover:bg-gray-500');
            // 为当前点击的 link 添加激活状态的特定样式
            link.classList.add('active', 'bg-blue-500', 'border-blue-500', 'cursor-default', 'font-bold', 'text-white');

            const activeTabContent = document.getElementById(tabId);
            activeTabContent.classList.remove('hidden');
            activeTabContent.classList.add('flex', 'flex-col');
        });
    });

    // --- WebSocket Logic ---
    const ws = new WebSocket(`ws://${window.location.host}${baseUrl}/ws`);

    // Initialize message display and get its functions
    const { tagMessage, allMessages, filterAndDisplayMessages, uniqueEvents, updateEventFilterOptions } = initMessageDisplay(
        document.getElementById('messages'),
        document.getElementById('event-filter-container'),
        document.getElementById('selected-events'),
        document.getElementById('event-options'),
        document.getElementById('clear-event-filter'),
        document.getElementById('clear-messages'),
        ws
    );

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

    // Initialize the message builder UI
    initMessageBuilder(
        messageBuilderSelect,
        builderFieldsDiv,
        sendBuilderMessageButton,
        builderPreview,
        sendMessage
    );

    // Initialize JSON message sender
    initJsonMessageSender(
        document.getElementById('message-input'),
        document.getElementById('send-message-button'),
        document.getElementById('format-message-button'),
        sendMessage
    );
});