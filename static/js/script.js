// Hospital Management System - Custom JavaScript

$(document).ready(function() {
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // Confirm delete actions
    $('.confirm-delete').click(function(e) {
        if (!confirm('Are you sure you want to delete this item?')) {
            e.preventDefault();
        }
    });
    
    // Form validation (exclude chatbot form which uses AJAX)
    $('form').not('#chatForm').submit(function() {
        $(this).find('button[type="submit"]').prop('disabled', true);
        $(this).find('button[type="submit"]').html('<span class="loading"></span> Processing...');
    });
    
    // Dashboard date/time display
    updateDateTime();
    setInterval(updateDateTime, 1000);
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Table row click to expand details
    $('.expandable-row').click(function() {
        $(this).next('.detail-row').toggle();
    });
    
    // Search functionality for tables
    $('#tableSearch').on('keyup', function() {
        var value = $(this).val().toLowerCase();
        $('#dataTable tbody tr').filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
        });
    });
    
    // Pagination for tables (simple client-side)
    paginateTable('.paginated-table', 10);
    
    // Statistics animation on page load
    $('.stat-card h2').each(function() {
        var $this = $(this);
        var countTo = $this.text();
        
        $({ countNum: 0 }).animate({
            countNum: countTo
        }, {
            duration: 1000,
            easing: 'linear',
            step: function() {
                $this.text(Math.floor(this.countNum));
            },
            complete: function() {
                $this.text(this.countNum);
            }
        });
    });
});

// Update date and time
function updateDateTime() {
    var now = new Date();
    var dateString = now.toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
    var timeString = now.toLocaleTimeString('en-US');
    
    $('#currentDate').text(dateString);
    $('#currentTime').text(timeString);
}

// Simple pagination function
function paginateTable(tableClass, rowsPerPage) {
    var $table = $(tableClass);
    var $tbody = $table.find('tbody');
    var $rows = $tbody.find('tr');
    var totalRows = $rows.length;
    var totalPages = Math.ceil(totalRows / rowsPerPage);
    var currentPage = 1;
    
    // Hide all rows except first page
    $rows.hide();
    $rows.slice(0, rowsPerPage).show();
    
    // Create pagination controls
    var paginationHtml = '<nav><ul class="pagination justify-content-center mt-3">';
    paginationHtml += '<li class="page-item" id="prevPage"><a class="page-link" href="#">Previous</a></li>';
    
    for (var i = 1; i <= totalPages; i++) {
        paginationHtml += '<li class="page-item page-num" data-page="' + i + '"><a class="page-link" href="#">' + i + '</a></li>';
    }
    
    paginationHtml += '<li class="page-item" id="nextPage"><a class="page-link" href="#">Next</a></li>';
    paginationHtml += '</ul></nav>';
    
    $table.after(paginationHtml);
    
    // Page number click
    $('.page-num').click(function(e) {
        e.preventDefault();
        currentPage = parseInt($(this).data('page'));
        var start = (currentPage - 1) * rowsPerPage;
        var end = start + rowsPerPage;
        
        $rows.hide();
        $rows.slice(start, end).show();
        
        $('.page-num').removeClass('active');
        $(this).addClass('active');
    });
    
    // Previous button
    $('#prevPage').click(function(e) {
        e.preventDefault();
        if (currentPage > 1) {
            currentPage--;
            $('.page-num[data-page="' + currentPage + '"]').click();
        }
    });
    
    // Next button
    $('#nextPage').click(function(e) {
        e.preventDefault();
        if (currentPage < totalPages) {
            currentPage++;
            $('.page-num[data-page="' + currentPage + '"]').click();
        }
    });
    
    // Set first page as active
    $('.page-num[data-page="1"]').addClass('active');
}

// Export table to CSV
function exportTableToCSV(tableId, filename) {
    var csv = [];
    var rows = document.querySelectorAll("#" + tableId + " tr");
    
    for (var i = 0; i < rows.length; i++) {
        var row = [], cols = rows[i].querySelectorAll("td, th");
        
        for (var j = 0; j < cols.length; j++) {
            row.push(cols[j].innerText);
        }
        
        csv.push(row.join(","));
    }
    
    downloadCSV(csv.join("\n"), filename);
}

function downloadCSV(csv, filename) {
    var csvFile;
    var downloadLink;
    
    csvFile = new Blob([csv], { type: "text/csv" });
    downloadLink = document.createElement("a");
    downloadLink.download = filename;
    downloadLink.href = window.URL.createObjectURL(csvFile);
    downloadLink.style.display = "none";
    document.body.appendChild(downloadLink);
    downloadLink.click();
}

// Print functionality
function printDiv(divId) {
    var printContents = document.getElementById(divId).innerHTML;
    var originalContents = document.body.innerHTML;
    
    document.body.innerHTML = printContents;
    window.print();
    document.body.innerHTML = originalContents;
    location.reload();
}

// Show loading overlay
function showLoading() {
    $('body').append('<div class="loading-overlay"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');
}

function hideLoading() {
    $('.loading-overlay').remove();
}

// Notification toast
function showToast(message, type = 'info') {
    var bgColor = 'bg-info';
    
    switch(type) {
        case 'success':
            bgColor = 'bg-success';
            break;
        case 'error':
        case 'danger':
            bgColor = 'bg-danger';
            break;
        case 'warning':
            bgColor = 'bg-warning';
            break;
    }
    
    var toast = `
        <div class="toast align-items-center text-white ${bgColor} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    $('body').append('<div class="toast-container position-fixed bottom-0 end-0 p-3">' + toast + '</div>');
    var toastElement = $('.toast').last();
    var bsToast = new bootstrap.Toast(toastElement);
    bsToast.show();
    
    setTimeout(function() {
        toastElement.remove();
    }, 5000);
}

// Data validation
function validateEmail(email) {
    var re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    var re = /^\+?[\d\s\-\(\)]+$/;
    return re.test(phone);
}

// Format date
function formatDate(date) {
    var d = new Date(date);
    var month = '' + (d.getMonth() + 1);
    var day = '' + d.getDate();
    var year = d.getFullYear();
    
    if (month.length < 2) month = '0' + month;
    if (day.length < 2) day = '0' + day;
    
    return [year, month, day].join('-');
}

// Debounce function for search
function debounce(func, wait) {
    var timeout;
    return function executedFunction(...args) {
        var later = function() {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize datepicker (if needed)
function initDatepickers() {
    $('input[type="date"]').each(function() {
        var today = new Date().toISOString().split('T')[0];
        $(this).attr('min', today);
    });
}

// Call on page load
initDatepickers();
