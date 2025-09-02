import { eventBus } from './event_bus.js';

/**
 * 集中式状态管理。
 */
class Store {
    constructor() {
        this.state = {
            messages: [],
            uniqueEvents: new Set(),
            selectedEvents: new Set(),
        };
    }

    /**
     * 获取当前状态的快照。
     * @returns {object} 当前状态的只读副本。
     */
    getState() {
        return { ...this.state };
    }

    /**
     * 添加一条新消息。
     * @param {object} message - 要添加的消息对象。
     */
    addMessage(message) {
        this.state.messages.push(message);
        if (message.tag && !this.state.uniqueEvents.has(message.tag)) {
            this.state.uniqueEvents.add(message.tag);
        }
        this.publishChange();
    }

    /**
     * 清除所有消息。
     */
    clearMessages() {
        this.state.messages = [];
        this.state.uniqueEvents.clear();
        this.state.selectedEvents.clear();
        this.publishChange();
    }

    /**
     * 更新事件筛选器。
     * @param {Set<string>} selectedEvents - 新的选择的事件集合。
     */
    updateSelectedEvents(selectedEvents) {
        this.state.selectedEvents = selectedEvents;
        this.publishChange();
    }

    /**
     * 发布状态变更事件。
     */
    publishChange() {
        eventBus.publish('state:changed', this.getState());
    }
}

// 导出一个单例
export const store = new Store();