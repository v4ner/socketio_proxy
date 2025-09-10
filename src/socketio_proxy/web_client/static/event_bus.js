/**
 * 一个简单的发布/订阅事件总线。
 * @class EventBus
 */
class EventBus {
    constructor() {
        this.events = {};
    }

    /**
     * 订阅一个事件。
     * @param {string} event - 事件名称。
     * @param {function} callback - 事件触发时执行的回调函数。
     * @returns {object} - 包含一个可以取消订阅的 unsubscribe 方法。
     */
    subscribe(event, callback) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        this.events[event].push(callback);
        return {
            unsubscribe: () => {
                this.events[event] = this.events[event].filter(cb => cb !== callback);
            }
        };
    }

    /**
     * 发布一个事件。
     * @param {string} event - 事件名称。
     * @param {*} data - 传递给回调函数的数据。
     */
    publish(event, data) {
        if (this.events[event]) {
            this.events[event].forEach(callback => callback(data));
        }
    }
}

// 导出一个单例
export const eventBus = new EventBus();