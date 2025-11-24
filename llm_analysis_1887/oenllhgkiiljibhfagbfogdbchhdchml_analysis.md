# CoCo Analysis: oenllhgkiiljibhfagbfogdbchhdchml

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 8 (all variants of the same flow)

---

## Sink: XMLHttpRequest_responseText_source → chrome_tabs_executeScript_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oenllhgkiiljibhfagbfogdbchhdchml/opgen_generated_files/bg.js
Line 332: XMLHttpRequest.prototype.responseText = 'sensitive_responseText';
Line 1045-1052: const html_special_chars = html => html.replace(/&/g, '&gt;')...
Line 1128: const data = is_html ? encodeURIComponent(xmlHttp.responseText) : encodeURIComponent(html_special_chars(xmlHttp.responseText));
Line 1130-1132: chrome.tabs.executeScript(...code: decodeURIComponent('${data}')...)

**Code:**

```javascript
// Background script - bodyModifier function (line 1112)
const bodyModifier = (tabId, changeInfo, tab) => {
  if (!tab.url.toLowerCase().startsWith('file://')) {
    return;
  }
  if (changeInfo.status.toLowerCase() !== 'complete') {
    return;
  }
  const encoding = encodingList.get(tabId) || defaultEncoding;
  if (!encoding) {
    return;
  }

  // Fetch the local file that user opened in their browser
  let xmlHttp = new XMLHttpRequest();
  xmlHttp.overrideMimeType(`text/plain; charset=${encoding}`);
  xmlHttp.onload = () => {
    const is_html = /\.html?$/.test(tab.url);
    // Sanitize and encode the content
    const data = is_html ? encodeURIComponent(xmlHttp.responseText) :
                          encodeURIComponent(html_special_chars(xmlHttp.responseText));

    // Re-render the page with correct encoding
    chrome.tabs.executeScript(tabId, {
      code: `const _t = document.open('text/${is_html ? 'html' : 'plain'}', 'replace');
      _t.write(${is_html ? `decodeURIComponent('${data}')` : `'<pre>' + decodeURIComponent('${data}') + '</pre>'`});
      _t.close();`,
      runAt: 'document_start',
    });
  };
  xmlHttp.open('GET', tab.url, true);  // Fetches the same file:// URL user opened
  xmlHttp.send();
};

// Triggered when user selects encoding from extension UI
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch(message.type) {
    case 'setEncoding': sendResponse(setEncoding(message.tabId, message.encoding)); break;
    // ... other cases
  }
});
```

**Classification:** FALSE POSITIVE

**Reason:** The XMLHttpRequest fetches the user's own local file (file:// URL) that they explicitly opened in their browser, not attacker-controlled data. The extension's purpose is to re-render the file with a different character encoding selected by the user through the extension popup. The user controls which file is opened, not an external attacker.
