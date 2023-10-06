
function updateCartQuantity(productId, customerId, action) {
    $.ajax({
        url: `/updatecartquantity/${productId}/${customerId}/${action}/`,
        method: 'POST',
        success: function(response) {
            if (response.status) {
                Swal.fire({
                    title: 'Increased',
                    text: 'Your cart item has been updated',
                    icon: 'success',
                    timer: 5000
                });
            }
        },
        error: function(xhr, status, error) {
            console.log(error);
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Find the first alert element with the 'alert' class
    var alertElement = document.querySelector('.alert');
  
    // Check if an alert element exists
    if (alertElement) {
      // Remove the alert after 5 seconds (5000 milliseconds)
      setTimeout(function() {
        alertElement.remove();
      }, 5000);
    }
  });