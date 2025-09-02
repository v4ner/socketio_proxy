import { messageBuilders } from './message_builders.js';
import { eventBus } from './event_bus.js';

export function initMessageBuilder(selectSelector, fieldsSelector, sendButtonSelector, previewSelector) {
    const messageBuilderSelect = document.querySelector(selectSelector);
    const builderFieldsDiv = document.querySelector(fieldsSelector);
    const sendBuilderMessageButton = document.querySelector(sendButtonSelector);
    const builderPreview = document.querySelector(previewSelector);

    if (!messageBuilderSelect || !builderFieldsDiv || !sendBuilderMessageButton || !builderPreview) {
        console.error('Message builder elements not found');
        return;
    }

    function populateBuilderSelect() {
        Object.keys(messageBuilders).forEach(name => {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name;
            messageBuilderSelect.appendChild(option);
        });
    }

    function generateBuilderFields(builderName) {
        builderFieldsDiv.innerHTML = '';
        const builder = messageBuilders[builderName];
        if (!builder) return;

        const params = builder.params;
        Object.keys(params).forEach(key => {
            const fieldGroup = document.createElement('div');
            fieldGroup.className = 'mb-2';

            const label = document.createElement('label');
            label.className = 'block text-sm font-medium text-gray-700';
            label.textContent = key;
            label.htmlFor = `builder-input-${key}`;

            const input = document.createElement('input');
            input.type = 'text';
            input.id = `builder-input-${key}`;
            input.name = key;
            input.value = params[key];
            input.className = 'mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500';

            fieldGroup.appendChild(label);
            fieldGroup.appendChild(input);
            builderFieldsDiv.appendChild(fieldGroup);
        });
    }

    function updateJsonPreview() {
        const builderName = messageBuilderSelect.value;
        const builder = messageBuilders[builderName];
        if (!builder) {
            builderPreview.textContent = '';
            return;
        }

        const data = {};
        const inputs = builderFieldsDiv.querySelectorAll('input');
        inputs.forEach(input => {
            let value = input.value;
            if (value.toLowerCase() === 'true') {
                value = true;
            } else if (value.toLowerCase() === 'false') {
                value = false;
            } else if (input.name !== 'Password' && !isNaN(value) && value.trim() !== '') {
                value = Number(value);
            }
            data[input.name] = value;
        });

        const message = builder.build(data);
        builderPreview.textContent = JSON.stringify(message, null, 2);
    }

    messageBuilderSelect.addEventListener('change', (e) => {
        generateBuilderFields(e.target.value);
        updateJsonPreview();
    });

    sendBuilderMessageButton.addEventListener('click', () => {
        const builderName = messageBuilderSelect.value;
        const builder = messageBuilders[builderName];
        if (!builder) return;

        const data = {};
        const inputs = builderFieldsDiv.querySelectorAll('input');
        inputs.forEach(input => {
            let value = input.value;
            if (value.toLowerCase() === 'true') {
                value = true;
            } else if (value.toLowerCase() === 'false') {
                value = false;
            } else if (input.name !== 'Password' && !isNaN(value) && value.trim() !== '') {
                value = Number(value);
            }
            data[input.name] = value;
        });

        const message = builder.build(data);
        eventBus.publish('ui:sendMessage', message);
    });

    // Initializations
    populateBuilderSelect();
    generateBuilderFields(messageBuilderSelect.value);
    updateJsonPreview();
    builderFieldsDiv.addEventListener('input', updateJsonPreview);
}