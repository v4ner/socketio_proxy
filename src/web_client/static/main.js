import { initServices } from './services.js';
import { initMessageDisplay } from './message_display.js';
import { initJsonMessageSender } from './json_message_sender.js';
import { initMessageBuilder } from './message_builder_ui.js';
import { initEventFilter } from './event_filter.js';
import { initTabs } from './tabs.js';
import { eventBus } from './event_bus.js';

document.addEventListener('DOMContentLoaded', () => {
    // 初始化所有服务
    initServices();

    // 初始化UI模块
    initTabs('.tab-link', '.tab-content');
    initMessageDisplay('#messages', '#clear-messages');
    initEventFilter('#event-filter-container', '#clear-event-filter');
    initJsonMessageSender('#message-input', '#send-message-button', '#format-message-button');
    initMessageBuilder('#message-builder-select', '#builder-fields', '#send-builder-message-button', '#builder-preview');

    // 处理重启按钮
    const restartSioButton = document.getElementById('restart-sio-button');
    restartSioButton.addEventListener('click', () => {
        eventBus.publish('ui:restartSio');
    });
});