// static/js/main.js
// Common JavaScript functions for the access control system

// Global utility functions
function getCookieValue(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function showLoading(element) {
    element.innerHTML = '<div class="loading"></div> Cargando...';
}

function hideLoading(element, originalContent) {
    element.innerHTML = originalContent;
}

// API helper functions
async function apiRequest(method, url, data = null, headers = {}) {
    const token = getCookieValue('access_token');
    
    if (!token) {
        window.location.href = '/admin/login';
        return;
    }
    
    const defaultHeaders = {
        'Authorization': token,
        'Content-Type': 'application/json',
        ...headers
    };
    
    try {
        const config = {
            method: method,
            url: url,
            headers: defaultHeaders
        };
        
        if (data) {
            config.data = data;
        }
        
        const response = await axios(config);
        return response.data;
    } catch (error) {
        console.error(`API Error (${method} ${url}):`, error);
        
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
            window.location.href = '/admin/login';
        }
        
        throw error;
    }
}

// Notification system
function showNotification(message, type = 'info', duration = 5000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (alertDiv.parentElement) {
            alertDiv.remove();
        }
    }, duration);
}

// Form validation helpers
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validateDocument(document) {
    // Basic document validation - only numbers and letters
    const documentRegex = /^[a-zA-Z0-9]+$/;
    return documentRegex.test(document) && document.length >= 5;
}

function validateRequired(value) {
    return value && value.trim().length > 0;
}

// Table helpers
function sortTable(table, column, ascending = true) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aVal = a.cells[column].textContent.trim();
        const bVal = b.cells[column].textContent.trim();
        
        if (ascending) {
            return aVal.localeCompare(bVal, undefined, { numeric: true });
        } else {
            return bVal.localeCompare(aVal, undefined, { numeric: true });
        }
    });
    
    rows.forEach(row => tbody.appendChild(row));
}

function filterTable(table, searchTerm, columns = []) {
    const tbody = table.querySelector('tbody');
    const rows = tbody.querySelectorAll('tr');
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        let showRow = false;
        
        if (columns.length === 0) {
            // Search all columns
            showRow = Array.from(cells).some(cell => 
                cell.textContent.toLowerCase().includes(searchTerm.toLowerCase())
            );
        } else {
            // Search specific columns
            showRow = columns.some(colIndex => {
                if (cells[colIndex]) {
                    return cells[colIndex].textContent.toLowerCase().includes(searchTerm.toLowerCase());
                }
                return false;
            });
        }
        
        row.style.display = showRow ? '' : 'none';
    });
}

// Modal helpers
function showModal(modalId) {
    const modal = new bootstrap.Modal(document.getElementById(modalId));
    modal.show();
}

function hideModal(modalId) {
    const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
    if (modal) {
        modal.hide();
    }
}

// Confirmation dialog
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Date helpers
function getMonthDateRange(month, year) {
    const start = new Date(year, month - 1, 1);
    const end = new Date(year, month, 0);
    return { start, end };
}

function isDateInRange(date, startDate, endDate) {
    const checkDate = new Date(date);
    return checkDate >= startDate && checkDate <= endDate;
}

// Export/Import helpers
function exportToCSV(data, filename) {
    const csv = data.map(row => 
        Object.values(row).map(value => `"${value}"`).join(',')
    ).join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

// Print helpers
function printElement(elementId) {
    const element = document.getElementById(elementId);
    const printWindow = window.open('', '_blank');
    
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Imprimir</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body { margin: 20px; }
                .no-print { display: none !important; }
            </style>
        </head>
        <body>
            ${element.innerHTML}
        </body>
        </html>
    `);
    
    printWindow.document.close();
    printWindow.print();
    printWindow.close();
}

// Local storage helpers (for settings, preferences, etc.)
function saveToLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
        console.error('Error saving to localStorage:', error);
    }
}

function loadFromLocalStorage(key, defaultValue = null) {
    try {
        const value = localStorage.getItem(key);
        return value ? JSON.parse(value) : defaultValue;
    } catch (error) {
        console.error('Error loading from localStorage:', error);
        return defaultValue;
    }
}

// Theme helpers
function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.body.setAttribute('data-theme', newTheme);
    saveToLocalStorage('theme', newTheme);
}

function initializeTheme() {
    const savedTheme = loadFromLocalStorage('theme', 'light');
    document.body.setAttribute('data-theme', savedTheme);
}

// Initialize common functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme
    initializeTheme();
    
    // Add search functionality to tables if search input exists
    const searchInput = document.querySelector('.table-search');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const table = document.querySelector('.table');
            if (table) {
                filterTable(table, e.target.value);
            }
        });
    }
    
    // Add loading states to buttons
    const buttons = document.querySelectorAll('.btn-loading');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="loading"></span> Cargando...';
            this.disabled = true;
            
            // Re-enable after 3 seconds (fallback)
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 3000);
        });
    });
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentElement) {
                alert.remove();
            }
        }, 5000);
    });
});

// Global error handler
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
});

// Global unhandled promise rejection handler
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
});
