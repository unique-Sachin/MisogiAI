// Expense Tracker JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeFormValidation();
    initializeCategoryFilter();
    initializeDeleteFunctionality();
});

// Form validation
function initializeFormValidation() {
    const form = document.getElementById('expenseForm');
    
    if (form) {
        form.addEventListener('submit', function(event) {
            const amount = document.getElementById('amount');
            const category = document.getElementById('category');
            const description = document.getElementById('description');
            
            let isValid = true;
            
            // Reset previous validation states
            form.classList.remove('was-validated');
            
            // Amount validation
            if (!amount.value || parseFloat(amount.value) <= 0) {
                amount.setCustomValidity('Please enter a positive amount.');
                isValid = false;
            } else {
                amount.setCustomValidity('');
            }
            
            // Category validation
            if (!category.value) {
                category.setCustomValidity('Please select a category.');
                isValid = false;
            } else {
                category.setCustomValidity('');
            }
            
            // Description validation
            if (!description.value.trim()) {
                description.setCustomValidity('Please enter a description.');
                isValid = false;
            } else {
                description.setCustomValidity('');
            }
            
            if (!isValid) {
                event.preventDefault();
                event.stopPropagation();
                form.classList.add('was-validated');
                
                // Show error message
                showAlert('Please fill all fields correctly.', 'danger');
            } else {
                // Show loading state
                const submitBtn = form.querySelector('button[type="submit"]');
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
            }
        });
        
        // Real-time validation
        form.querySelectorAll('input, select').forEach(input => {
            input.addEventListener('input', function() {
                this.setCustomValidity('');
                this.classList.remove('is-invalid');
            });
        });
    }
}

// Category filter functionality
function initializeCategoryFilter() {
    const categoryFilter = document.getElementById('categoryFilter');
    const expensesTable = document.getElementById('expensesTable');
    
    if (categoryFilter && expensesTable) {
        categoryFilter.addEventListener('change', function() {
            const selectedCategory = this.value;
            const rows = expensesTable.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const rowCategory = row.getAttribute('data-category');
                
                if (selectedCategory === '' || rowCategory === selectedCategory) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
            
            // Update visible count
            updateVisibleCount();
        });
    }
}

// Delete expense functionality
function initializeDeleteFunctionality() {
    // Add event delegation for delete buttons
    document.addEventListener('click', function(event) {
        if (event.target.closest('.btn-danger')) {
            const button = event.target.closest('.btn-danger');
            const expenseId = button.getAttribute('onclick').match(/\d+/)[0];
            
            // Prevent default onclick
            event.preventDefault();
            
            // Show confirmation dialog
            showDeleteConfirmation(expenseId);
        }
    });
}

// Delete expense function
async function deleteExpense(expenseId) {
    try {
        const response = await fetch(`/expenses/${expenseId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            // Remove the row from table
            const row = document.querySelector(`button[onclick="deleteExpense(${expenseId})"]`).closest('tr');
            row.style.animation = 'fadeOut 0.3s ease-out';
            
            setTimeout(() => {
                row.remove();
                updateVisibleCount();
                showAlert('Expense deleted successfully!', 'success');
                
                // Reload page to update summary
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            }, 300);
        } else {
            throw new Error('Failed to delete expense');
        }
    } catch (error) {
        console.error('Error deleting expense:', error);
        showAlert('Failed to delete expense. Please try again.', 'danger');
    }
}

// Show delete confirmation dialog
function showDeleteConfirmation(expenseId) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Confirm Delete</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>Are you sure you want to delete this expense? This action cannot be undone.</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-danger" onclick="confirmDelete(${expenseId})">Delete</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    
    // Clean up modal after hiding
    modal.addEventListener('hidden.bs.modal', function() {
        document.body.removeChild(modal);
    });
}

// Confirm delete function
function confirmDelete(expenseId) {
    deleteExpense(expenseId);
    
    // Close modal
    const modal = document.querySelector('.modal.show');
    if (modal) {
        const bootstrapModal = bootstrap.Modal.getInstance(modal);
        bootstrapModal.hide();
    }
}

// Update visible count in filter
function updateVisibleCount() {
    const visibleRows = document.querySelectorAll('#expensesTable tbody tr[style=""], #expensesTable tbody tr:not([style])');
    const totalRows = document.querySelectorAll('#expensesTable tbody tr').length;
    
    // You can add a count display here if needed
    console.log(`Showing ${visibleRows.length} of ${totalRows} expenses`);
}

// Show alert messages
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.container-fluid');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alert.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto dismiss after 3 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.classList.remove('show');
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 150);
        }
    }, 3000);
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Add fade out animation
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from { opacity: 1; transform: translateX(0); }
        to { opacity: 0; transform: translateX(-100%); }
    }
`;
document.head.appendChild(style); 