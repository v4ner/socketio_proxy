// =================================================================
// Message Formatters
// =================================================================

/**
 * 格式化消息以进行显示。
 * @param {object} message - 原始消息对象。
 * @returns {object} - 包含 compactContent 和 fullContent 的格式化消息。
 */
export function formatMessageForDisplay(message) {
    const eventType = message.event || 'unknown';
    const formatter = messageFormatters[eventType] || messageFormatters.default;
    return formatter(message);
}

// 默认格式化器
const defaultFormatter = (message) => {
    return {
        compactContent: JSON.stringify(message),
        fullContent: JSON.stringify(message, null, 2)
    };
};

// =================================================================
// Custom Formatters - Add custom formatters here
// =================================================================
// 示例:
// const customFormatter = (message) => {
//     const data = message.data || {};
//     return {
//         compactContent: `Custom Event: ${data.info}`,
//         fullContent: JSON.stringify(message, null, 2)
//     };
// };

const messageFormatters = {
    'default': defaultFormatter,
    // 'CustomEvent': customFormatter, // 在这里注册自定义格式化器
};