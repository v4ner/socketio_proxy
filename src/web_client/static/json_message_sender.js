export function initJsonMessageSender(messageInput, sendMessageButton, formatMessageButton, sendMessage) {
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
}