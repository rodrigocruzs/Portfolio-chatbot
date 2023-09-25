const connectPlaid = async () => {
    {
		fetch('/api/create_link_token', {
			method: 'POST'
		})
		.then(response => response.json())
		.then(data => {
			const linkToken = data.link_token;
			const handler = Plaid.create({
				token: linkToken,
				onSuccess: (public_token, metadata) => {
					// Exchange the public token for an access token
					fetch('/api/set_access_token', {
						method: 'POST',
						headers: {
							'Content-Type': 'application/json'
						},
						body: JSON.stringify({ public_token: public_token })
					})
					.then(response => response.json())
					.then(data => {
						if (data.access_token) {
							// Access token obtained successfully, now fetch the investment data

							// Fetch investment transactions
							fetch('/api/investments_transactions')
								.then(response => {
									if (!response.ok) {
										throw new Error('Network response was not ok');
									}
									return response.json();
								})
								.then(transactionsData => {
									console.log(transactionsData);
									// Do something with the investment transactions data, or store it
								})
								.catch(error => {
									console.error('Error fetching investment transactions:', error);
								});

							// Fetch holdings
							fetch('/api/holdings')
								.then(response => response.json())
								.then(holdingsData => {
									console.log(holdingsData);
									// Do something with the holdings data, or store it
								})
								.catch(error => {
									console.error('Error fetching holdings:', error);
								});
								
							// Fetch accounts
							fetch('/api/accounts')
								.then(response => {
									if (!response.ok) {
										throw new Error('Network response was not ok');
									}
									return response.json();
								})
								.then(accountsData => {
									console.log(accountsData);
									// Do something with the accounts data, or store it
								})
								.catch(error => {
									console.error('Error fetching accounts:', error);
								});

							window.location.href = "/chat";
						} else {
							console.error('Error obtaining access token:', data.error);
						}
					})
					.catch(error => {
						console.error('Error exchanging public token for access token:', error);
					});
				},
				onLoad: () => { /* Handle load */ },
				onExit: (err, metadata) => { /* Handle exit */ },
				onEvent: (eventName, metadata) => { /* Handle events */ },
			});
			handler.open();
		})
		.catch(error => {
			console.error('Error fetching link token:', error);
		});
	}
}