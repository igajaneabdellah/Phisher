function checkEmail(emailBody) {
    fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email_text: emailBody })
    })
    .then(response => response.json())
    .then(data => {
        alert('This email is: ' + data.prediction);
        
        // Display URL check results
        let urls = Object.keys(data.url_checks);
        if (urls.length > 0) {
            let urlCheckResults = 'URL Checks:\n';
            urls.forEach(url => {
                urlCheckResults += `${url}: ${data.url_checks[url]}\n`;
            });
            alert(urlCheckResults);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
  }
  
  // Listen for messages from background script
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "analyzeEmail") {
      let emailBody = window.getSelection().toString();
      checkEmail(emailBody);
    }
  });
  