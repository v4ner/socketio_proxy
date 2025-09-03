import { initServices } from './services.js';
import { eventBus } from './event_bus.js';
import { store } from './store.js';
import { messageBuilders } from './message_builders.js';
import { formatMessageForDisplay } from './message_formatters.js';

// 将模块暴露给 Alpine.js
window.eventBus = eventBus;
window.store = store;
window.messageBuilders = messageBuilders;
window.formatMessageForDisplay = formatMessageForDisplay;

document.addEventListener('DOMContentLoaded', () => {
    // 初始化所有服务
    initServices();

    // UI 模块现在由 Alpine.js 负责初始化

    // 处理重启按钮
    const restartSioButton = document.getElementById('restart-sio-button');
    restartSioButton.addEventListener('click', () => {
        window.eventBus.publish('ui:restartSio');
    });
});