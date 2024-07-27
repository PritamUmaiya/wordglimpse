/* 
    NOTE: AI used in this function
    Handling tabs: Changing the url dynamically with selected tab
    The content in each tab will be loaded dynamically: Only after visiting the tab
*/

// Change the URL
function load_content(url) {
    history.pushState(null, null, url);
    activateTab(url);
}
function activateTab(url) {
    const tabs = {
        '/': 'home-tab',
        '/home': 'home-tab',
        '/following': 'following-tab',
        '/saved': 'saved-tab'
    };

    // Default to 'content-tab' if no match found
    const activeTabId = tabs[url] || 'content-tab';
    
    // Deactivate all tabs and panes
    document.querySelectorAll('.bottom-nav .btn').forEach(button => {
        button.classList.remove('active');
    });
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('show', 'active');
    });
    
    // Activate the selected tab and pane
    const activeTab = document.getElementById(activeTabId);
    if (activeTab) {
        activeTab.classList.add('active');
        document.querySelector(activeTab.getAttribute('data-bs-target')).classList.add('show', 'active');
    } else {
        document.querySelector('#content-tab-pane').classList.add('show', 'active');
    }
}
// Activate tab on initial load
window.addEventListener('DOMContentLoaded', () => {
    activateTab(window.location.pathname);
});
// Activate tab on back/forward navigation
window.addEventListener('popstate', () => {
    activateTab(window.location.pathname);
});