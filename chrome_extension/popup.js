document.addEventListener('DOMContentLoaded', function () {
    chrome.storage.local.get(['result'], function (data) {
      document.getElementById('result').innerText = JSON.stringify(data.result, null, 2);
    });
  });
  