import { eventBus } from './event_bus.js';
import { store } from './store.js';
import { formatMessageForDisplay } from './message_formatters.js';

const BASE_URL = window.BASE_URL;

/**
 * 标记消息，添加一个 'tag' 字段。
 * @param {object} message - 原始消息。
 * @returns {object} - 带有 'tag' 的消息。
 */
function tagMessage(message) {
    message.tag = message.event || 'unknown';
    return message;
}

/**
 * 处理收到的或发送的消息，将其添加到 store。
 * @param {object} message - 原始消息对象。
 */
function processAndStoreMessage(message) {
    const taggedMessage = tagMessage(message);
    const formattedMessage = formatMessageForDisplay(taggedMessage);
    store.addMessage({ ...taggedMessage, ...formattedMessage });
}

/**
 * API 服务，用于处理 HTTP 请求。
 */
const apiService = {
    /**
     * 发送消息到后端。
     * @param {object} messageObject - 要发送的消息。
     */
    sendMessage: (messageObject) => {
        console.log('Sending message via API:', messageObject);
        fetch(`${BASE_URL}/send_message`, {
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
            processAndStoreMessage(sentMessage);
        })
        .catch(error => {
            console.error('Error sending message:', error);
            alert(`发送消息失败: ${error.message}`);
        });
    },

    /**
     * 请求重启 Socket.IO 连接。
     */
    restartSio: () => {
        if (confirm('确定要重启Socket.IO连接吗？')) {
            fetch(`${BASE_URL}/restart_sio`, { method: 'POST' })
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
    }
};

/**
 * WebSocket 服务，用于处理 WebSocket 连接和事件。
 */
const webSocketService = {
    init: () => {
        const ws = new WebSocket(`ws://${window.location.host}${BASE_URL}/ws`);

        ws.onopen = (event) => {
            console.log('WebSocket connected:', event);
            processAndStoreMessage({ type: 'status', content: 'WebSocket connected!' });
        };

        ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                processAndStoreMessage(message);
            } catch (e) {
                console.error(`Received non-JSON message: ${event.data}`);
                processAndStoreMessage({ type: 'error', content: `Received non-JSON message: ${event.data}` });
            }
        };

        ws.onclose = (event) => {
            console.log('WebSocket disconnected:', event);
            processAndStoreMessage({ type: 'status', content: 'WebSocket disconnected!' });
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            processAndStoreMessage({ type: 'error', content: `WebSocket error: ${error.message || 'Unknown error'}` });
        };
    }
};

// 订阅UI事件来触发服务调用
eventBus.subscribe('ui:sendMessage', apiService.sendMessage);
eventBus.subscribe('ui:restartSio', apiService.restartSio);

export function initServices() {
    webSocketService.init();
    // apiService 不需要初始化，因为它只是一个方法集合
}