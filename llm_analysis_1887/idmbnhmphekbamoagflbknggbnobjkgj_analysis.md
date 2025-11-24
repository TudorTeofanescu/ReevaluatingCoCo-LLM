# CoCo Analysis: idmbnhmphekbamoagflbknggbnobjkgj

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 4 (all storage write sinks without retrieval to attacker)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/idmbnhmphekbamoagflbknggbnobjkgj/opgen_generated_files/bg.js
Line 1010: `chrome.storage.local.set({'token': request['token']}, ...);`
Line 1011: `chrome.storage.local.set({'username': request['username']}, ...);`
Line 1012: `chrome.storage.local.set({'picture': request['picture']}, ...);`
Line 1013: `chrome.storage.local.set({'access': request['access']}, ...);`

**Code:**

```javascript
// Background script (bg.js) - Line 1001
chrome.runtime.onMessageExternal.addListener(
    function(request, sender, sendResponse) {
        console.log(sender.url);

        // Check if message is from specific hurlons.com URLs
        if (sender.url == 'https://www.hurlons.com/my_account.php?logged' ||
            sender.url == 'https://www.hurlons.com/my_account.php' ||
            sender.url == 'https://www.hurlons.com/my_account.php?updated' ||
            sender.url == 'https://www.hurlons.com/toolbar/connexion.php?browser=Chrome')
        {
            console.log('Connexion information');
            // Store user credentials from external message
            chrome.storage.local.set({'token': request['token']}, ...); // ← attacker can control
            chrome.storage.local.set({'username': request['username']}, ...);
            chrome.storage.local.set({'picture': request['picture']}, ...);
            chrome.storage.local.set({'access': request['access']}, ...);
        }

        // No sendResponse with retrieved data
    }
);

// Line 977-979 - Token is retrieved but only used for backend API
chrome.storage.local.get(['token'], function(result) {
    Ping(tab.url, result.token, tab); // Sends to hardcoded backend
});

// Line 984-998 - Ping function
function Ping(url, session, tab) {
    fetch("https://www.hurlons.com/API/notes.php?ping="+encodeURIComponent(url),
          { method: 'GET' }) // ← sends to developer's hardcoded backend
    .then(response => response.json())
    .then(function(json_obj) {
        // Updates badge with backend response
        chrome.action.setBadgeText({ tabId: tab.id, text: total.toString()});
    });
}
```

**Manifest.json:**
```json
"externally_connectable": {
  "matches": ["https://*.hurlons.com/*"]
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation - storage poisoning without retrieval path to the attacker. While the whitelisted domain `https://*.hurlons.com/*` can send external messages to write arbitrary values to storage (token, username, picture, access), there is no code path that sends this stored data back to the attacker. The stored token is retrieved later (line 977) but only sent to the developer's hardcoded backend URL (`https://www.hurlons.com/API/notes.php`) in the Ping function, which is trusted infrastructure. The onMessageExternal handler does not call sendResponse with any retrieved storage data. According to the methodology, storage poisoning alone (storage.set without a retrieval path where the attacker can observe/retrieve the value) is NOT a vulnerability.
