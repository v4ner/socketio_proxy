import { eventBus } from './event_bus.js';
import { store } from './store.js';

function render(container, state) {
    const { uniqueEvents, selectedEvents } = state;
    const selectedEventsDiv = container.querySelector('#selected-events');
    const eventOptionsDiv = container.querySelector('#event-options');

    // 更新已选择的事件标签
    selectedEventsDiv.innerHTML = '';
    if (selectedEvents.size === 0) {
        selectedEventsDiv.innerHTML = '<span class="text-gray-500 px-1">选择事件...</span>';
    } else {
        selectedEvents.forEach(event => {
            const tag = document.createElement('span');
            tag.className = 'bg-gray-200 px-2 py-1 rounded-sm flex items-center gap-1';
            tag.textContent = event;
            const removeBtn = document.createElement('span');
            removeBtn.className = 'cursor-pointer font-bold text-gray-600 hover:text-black';
            removeBtn.textContent = 'x';
            removeBtn.onclick = (e) => {
                e.stopPropagation();
                const newSelected = new Set(selectedEvents);
                newSelected.delete(event);
                store.updateSelectedEvents(newSelected);
            };
            tag.appendChild(removeBtn);
            selectedEventsDiv.appendChild(tag);
        });
    }

    // 更新下拉选项
    eventOptionsDiv.innerHTML = '';
    uniqueEvents.forEach(event => {
        const option = document.createElement('div');
        option.className = 'px-2 py-1 cursor-pointer hover:bg-gray-100';
        option.textContent = event;
        option.dataset.event = event;
        if (selectedEvents.has(event)) {
            option.classList.add('bg-blue-50', 'font-bold');
        }
        option.onclick = () => {
            const newSelected = new Set(selectedEvents);
            if (newSelected.has(event)) {
                newSelected.delete(event);
            } else {
                newSelected.add(event);
            }
            store.updateSelectedEvents(newSelected);
        };
        eventOptionsDiv.appendChild(option);
    });
}

export function initEventFilter(containerSelector, clearButtonSelector) {
    const container = document.querySelector(containerSelector);
    const clearButton = document.querySelector(clearButtonSelector);
    const eventOptionsDiv = container.querySelector('#event-options');

    if (!container || !clearButton || !eventOptionsDiv) {
        console.error('Event filter elements not found');
        return;
    }

    // 订阅状态变更
    eventBus.subscribe('state:changed', (state) => {
        render(container, state);
    });

    // 处理下拉菜单的显示/隐藏
    container.addEventListener('click', () => {
        eventOptionsDiv.classList.toggle('hidden');
    });

    document.addEventListener('click', (e) => {
        if (!container.contains(e.target)) {
            eventOptionsDiv.classList.add('hidden');
        }
    });

    // 处理清除按钮
    clearButton.addEventListener('click', () => {
        store.updateSelectedEvents(new Set());
    });

    // 初始渲染
    render(container, store.getState());
}