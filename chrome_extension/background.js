chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "analyzeEmail",
    title: "Analyze Email for Phishing",
    contexts: ["selection"]
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "analyzeEmail") {
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: analyzeSelectedEmail,
      args: [info.selectionText]
    });
  }
});

function analyzeSelectedEmail(selectedText) {
  // Send the selected text to the backend for analysis
  fetch('http://localhost:5000/predict', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email_text: selectedText })
  })
  .then(response => response.json())
  .then(data => {
    // Display the phishing prediction result
    let resultMessage = `Email Analysis Result: ${data.prediction}`;
    
    // Display URL check results if any
    if (data.url_checks) {
      resultMessage += '\n\nURL Checks:\n';
      for (const [url, result] of Object.entries(data.url_checks)) {
        resultMessage += `${url}: ${result}\n`;
      }
    }
    
    alert(resultMessage);
  })
  .catch(error => console.error('Error:', error));
}
