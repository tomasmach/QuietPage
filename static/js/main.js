/**
 * QuietPage - Main JavaScript
 * Vanilla JS utilities for enhanced user experience
 * 
 * Structure:
 * 1. Django Messages Auto-Hide & Close
 * 2. Form Helpers (Character Count, Word Count)
 * 3. Auto-Save Indicator
 * 4. Utility Functions
 */

// ============================================
// 1. DJANGO MESSAGES AUTO-HIDE & CLOSE
// ============================================

/**
 * Initialize Django messages functionality
 * - Auto-hide after 5 seconds (except errors)
 * - Close button functionality
 */
function initMessages() {
    const messagesContainer = document.querySelector('.messages-container');
    if (!messagesContainer) return;

    const messages = messagesContainer.querySelectorAll('.message');
    
    messages.forEach((message) => {
        // Close button functionality
        const closeBtn = message.querySelector('.message-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                hideMessage(message);
            });
        }

        // Auto-hide messages (except errors)
        const isError = message.classList.contains('message-error') || 
                       message.classList.contains('message-danger');
        
        if (!isError) {
            setTimeout(() => {
                hideMessage(message);
            }, 5000); // 5 seconds
        }
    });
}

/**
 * Hide message with fade-out animation
 * @param {HTMLElement} message - Message element to hide
 */
function hideMessage(message) {
    message.style.animation = 'slideOut 0.3s ease';
    
    setTimeout(() => {
        message.remove();
        
        // Remove container if no messages left
        const container = document.querySelector('.messages-container');
        if (container && container.querySelectorAll('.message').length === 0) {
            container.remove();
        }
    }, 300);
}

// Add slideOut animation dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ============================================
// 2. FORM HELPERS
// ============================================

/**
 * Character counter for textareas
 * Usage: Add data-character-count="true" to textarea
 * Displays character count below textarea
 */
function initCharacterCount() {
    const textareas = document.querySelectorAll('textarea[data-character-count]');
    
    textareas.forEach((textarea) => {
        // Create counter element
        const counter = document.createElement('div');
        counter.className = 'form-help character-count';
        counter.setAttribute('aria-live', 'polite');
        
        // Insert after textarea
        textarea.parentNode.insertBefore(counter, textarea.nextSibling);
        
        // Update count function
        const updateCount = () => {
            const count = textarea.value.length;
            const maxLength = textarea.getAttribute('maxlength');
            
            if (maxLength) {
                counter.textContent = `${count} / ${maxLength} znaků`;
            } else {
                counter.textContent = `${count} znaků`;
            }
        };
        
        // Initial count
        updateCount();
        
        // Update on input
        textarea.addEventListener('input', updateCount);
    });
}

/**
 * Word counter for textareas
 * Usage: Add data-word-count="true" to textarea
 * Displays word count below textarea
 */
function initWordCount() {
    const textareas = document.querySelectorAll('textarea[data-word-count]');
    
    textareas.forEach((textarea) => {
        // Create counter element
        const counter = document.createElement('div');
        counter.className = 'form-help word-count';
        counter.setAttribute('aria-live', 'polite');
        
        // Insert after textarea
        textarea.parentNode.insertBefore(counter, textarea.nextSibling);
        
        // Update count function
        const updateCount = () => {
            const text = textarea.value.trim();
            const wordCount = text ? text.split(/\s+/).length : 0;
            
            if (wordCount === 0) {
                counter.textContent = '0 slov';
            } else if (wordCount === 1) {
                counter.textContent = '1 slovo';
            } else if (wordCount >= 2 && wordCount <= 4) {
                counter.textContent = `${wordCount} slova`;
            } else {
                counter.textContent = `${wordCount} slov`;
            }
        };
        
        // Initial count
        updateCount();
        
        // Update on input
        textarea.addEventListener('input', updateCount);
    });
}

// ============================================
// 3. AUTO-SAVE INDICATOR
// ============================================

/**
 * Show save indicator (for auto-save features)
 * @param {string} message - Message to display (default: 'Uloženo')
 * @param {string} type - Type: 'success', 'saving', 'error'
 */
function showSaveIndicator(message = 'Uloženo', type = 'success') {
    // Remove existing indicator
    const existing = document.querySelector('.save-indicator');
    if (existing) existing.remove();
    
    // Create indicator
    const indicator = document.createElement('div');
    indicator.className = `save-indicator save-indicator-${type}`;
    indicator.textContent = message;
    indicator.setAttribute('role', 'status');
    indicator.setAttribute('aria-live', 'polite');
    
    // Add to body
    document.body.appendChild(indicator);
    
    // Auto-hide after 2 seconds
    setTimeout(() => {
        indicator.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => indicator.remove(), 300);
    }, 2000);
}

// Add save indicator styles dynamically
const saveIndicatorStyle = document.createElement('style');
saveIndicatorStyle.textContent = `
    .save-indicator {
        position: fixed;
        bottom: 24px;
        right: 24px;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 600;
        box-shadow: var(--shadow-soft);
        z-index: 9998;
        animation: fadeIn 0.3s ease;
    }
    
    .save-indicator-success {
        background-color: #E8F5E9;
        color: #2E7D32;
        border-left: 4px solid #4CAF50;
    }
    
    .save-indicator-saving {
        background-color: var(--bg-card);
        color: var(--text-main);
        border-left: 4px solid var(--primary);
    }
    
    .save-indicator-error {
        background-color: #FFEBEE;
        color: #C62828;
        border-left: 4px solid #F44336;
    }
    
    @media (prefers-color-scheme: dark) {
        .save-indicator-success {
            background-color: rgba(76, 175, 80, 0.15);
            color: #81C784;
        }
        
        .save-indicator-error {
            background-color: rgba(244, 67, 54, 0.15);
            color: #E57373;
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeOut {
        from { opacity: 1; transform: translateY(0); }
        to { opacity: 0; transform: translateY(10px); }
    }
    
    @media (max-width: 768px) {
        .save-indicator {
            bottom: 16px;
            right: 16px;
            left: 16px;
            text-align: center;
        }
    }
`;
document.head.appendChild(saveIndicatorStyle);

// ============================================
// 4. UTILITY FUNCTIONS
// ============================================

/**
 * Debounce function - limits how often a function can be called
 * Useful for auto-save on input events
 * 
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 * 
 * Usage:
 * const debouncedSave = debounce(() => saveData(), 1000);
 * textarea.addEventListener('input', debouncedSave);
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Get CSRF token from cookies (for Django AJAX requests)
 * @returns {string|null} CSRF token or null
 */
function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    
    return cookieValue;
}

/**
 * Format date to Czech locale
 * @param {Date|string} date - Date to format
 * @returns {string} Formatted date
 */
function formatDateCzech(date) {
    const d = new Date(date);
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    };
    return d.toLocaleDateString('cs-CZ', options);
}

/**
 * Format time to Czech locale
 * @param {Date|string} date - Date to format
 * @returns {string} Formatted time
 */
function formatTimeCzech(date) {
    const d = new Date(date);
    const options = { 
        hour: '2-digit', 
        minute: '2-digit' 
    };
    return d.toLocaleTimeString('cs-CZ', options);
}

// ============================================
// INITIALIZATION
// ============================================

/**
 * Initialize all functionality when DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
    // Initialize messages
    initMessages();
    
    // Initialize form helpers
    initCharacterCount();
    initWordCount();
    
    console.log('✨ QuietPage JavaScript initialized');
});

// Export functions for use in other scripts (optional)
window.QuietPage = {
    showSaveIndicator,
    debounce,
    getCSRFToken,
    formatDateCzech,
    formatTimeCzech,
    hideMessage
};
