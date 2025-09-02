import { eventBus } from './event_bus.js';
import { store } from './store.js';

/**
 * 渲染消息列表。
 * @param {HTMLElement} messagesDiv - 用于显示消息的 div 元素。
 * @param {object} state - 当前的应用状态。
 */
function render(messagesDiv, state) {
    const { messages, selectedEvents } = state;
    messagesDiv.innerHTML = '';

    messages.forEach(message => {
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
            compactContent.className = 'flex-grow whitespace-pre-wrap break-words overflow-hidden text-ellipsis mr-1';
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

    // 自动滚动到底部
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

/**
 * 初始化消息显示模块。
 * @param {string} messagesSelector - 消息容器的 CSS 选择器。
 * @param {string} clearButtonSelector - 清除消息按钮的 CSS 选择器。
 */
export function initMessageDisplay(messagesSelector, clearButtonSelector) {
    const messagesDiv = document.querySelector(messagesSelector);
    const clearMessagesButton = document.querySelector(clearButtonSelector);

    if (!messagesDiv || !clearMessagesButton) {
        console.error('Message display elements not found');
        return;
    }

    // 订阅状态变更事件
    eventBus.subscribe('state:changed', (state) => {
        render(messagesDiv, state);
    });

    // 监听清除按钮点击事件
    clearMessagesButton.addEventListener('click', () => {
        // 发布一个事件来请求清除消息，而不是直接操作 store
        eventBus.publish('ui:clearMessages');
    });

    // 初始渲染
    render(messagesDiv, store.getState());
}

// 在 store 模块中添加对 'ui:clearMessages' 事件的响应
eventBus.subscribe('ui:clearMessages', () => {
    store.clearMessages();
});