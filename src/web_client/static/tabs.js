export function initTabs(tabLinkSelector, tabContentSelector) {
    const tabLinks = document.querySelectorAll(tabLinkSelector);
    const tabContents = document.querySelectorAll(tabContentSelector);

    tabLinks.forEach(link => {
        link.addEventListener('click', () => {
            const tabId = link.getAttribute('data-tab');

            tabLinks.forEach(innerLink => {
                innerLink.classList.remove('active', 'bg-blue-500', 'border-blue-500', 'cursor-default', 'font-bold', 'text-white');
                innerLink.classList.add('bg-gray-400', 'border-gray-400', 'border-b', 'text-gray-800', 'hover:bg-gray-500');
            });

            tabContents.forEach(content => {
                content.classList.remove('flex', 'flex-col');
                content.classList.add('hidden');
            });

            link.classList.remove('bg-gray-400', 'border-gray-400', 'border-b', 'text-gray-800', 'hover:bg-gray-500');
            link.classList.add('active', 'bg-blue-500', 'border-blue-500', 'cursor-default', 'font-bold', 'text-white');

            const activeTabContent = document.getElementById(tabId);
            activeTabContent.classList.remove('hidden');
            activeTabContent.classList.add('flex', 'flex-col');
        });
    });
}