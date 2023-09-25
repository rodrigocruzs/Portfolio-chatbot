var stripe = Stripe('pk_live_51NrlkKCp04lVZoC1r6qrv9pFiFUhVwVsgc6mZHw6OXgHkEa4bDJxJDQpG9V0WBqwUQWbyXfMT1sYr8ZjAkP2YSzV00V7NsD73b');
var checkoutButton = document.getElementById('checkout-button');

var checkoutButton = document.getElementById('checkout-button');
var premiumButton = document.getElementById('premium-button');

checkoutButton.addEventListener('click', (event) => {
    event.preventDefault();
    
    fetch('/create-checkout-session', {
        method: 'POST',
    })
    .then(response => response.json())
    .then((session) => {
        return stripe.redirectToCheckout({ sessionId: session.id });
    })
    .then((result) => {
        if (result.error) {
            alert(result.error.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});

premiumButton.addEventListener('click', (event) => {
    console.log('Premium button clicked');
    event.preventDefault();
    
    // Here, you can either use the same fetch call as above, 
    // or define a new fetch call if the endpoint or parameters are different
    fetch('/create-checkout-session', {
        method: 'POST',
    })
    .then(response => response.json())
    .then((session) => {
        return stripe.redirectToCheckout({ sessionId: session.id });
    })
    .then((result) => {
        if (result.error) {
            alert(result.error.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});