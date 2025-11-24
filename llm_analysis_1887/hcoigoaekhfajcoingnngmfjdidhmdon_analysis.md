# CoCo Analysis: hcoigoaekhfajcoingnngmfjdidhmdon

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (multiple traces)

---

## Sink 1 & 2: document_eventListener_wvHandshake → chrome_storage_local_set_sink

**CoCo Trace:**
From used_time.txt:
```
(['24691', '24702', '24757', '68407', '73412', '74412', '79676'], 'document_eventListener_wvHandshake')
from document_eventListener_wvHandshake to chrome_storage_local_set_sink

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hcoigoaekhfajcoingnngmfjdidhmdon/opgen_generated_files/cs_0.js
Line 481	document.addEventListener('wvHandshake', function(request) {
Line 482	    var response = request.detail;
Line 485	    if (request.detail.extension)

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hcoigoaekhfajcoingnngmfjdidhmdon/opgen_generated_files/bg.js
Line 1195	        checkBeforeCreate(msg.request, tab, msg.domain);
Line 1857	                            let chain_id = request.username.split(':')[0].toUpperCase();
Line 1281	                    var user_arr = data.username.replace(/,/g, ' ').trim().split(' ');
```

**Code:**

```javascript
// Content script cs_0.js - Lines 481-488 (wvHandshake event - NOT the main attack vector)
document.addEventListener('wvHandshake', function(request) {
    var response = request.detail;
    response.name = chrome.runtime.getManifest().name;
    response.version = chrome.runtime.getManifest().version;
    if (request.detail.extension)
      chrome.runtime.sendMessage(request.detail.extension, response).catch(e=>{}); else
        window.postMessage({ type: "wvHandshake", response });
});

// Content script cs_0.js - Lines 491-515 (wvRequest event - MAIN entry point)
document.addEventListener('wvRequest', function(request) {
    var req = request.detail; // ← attacker-controlled from webpage
    var domain = window.location.hostname;
    if (domain == '127.0.0.1') domain = 'localhost';
    if (!["", "80", "443"].includes(window.location.port)) domain += ":"+window.location.port;

    if (req.username) {
        req.username = req.username.toLowerCase();
        if (!req.username.includes(":")) req.username = "stm:" + req.username;
    }
    if (req.appid) req.appid = req.appid.substring(0,25).replace(/ /g,'');
    if (req.reason) req.reason = req.reason.substring(0,25).replace(/ /g,'');
    if (domain.includes('localhost') && req.appid) domain += ":"+escapeHtml(req.appid);
    req.domain = domain;

    if (validate(req)) {
        chrome.runtime.sendMessage({
            command: "sendRequest",
            request: req, // ← attacker data flows here
            domain,
            request_id: req.request_id
        }).catch(e=>{});
    }
});

// Background bg.js - Lines 1179-1195 (Message handler)
} else if (msg.command == "sendRequest") {
    if (id_win != null || request_queue.length > 0) {
        var req_obj = { tab: sender.tab.id, msg };
        request_queue.push(req_obj);
        let message = {
            command: "queueStats",
            queue_len: request_queue.length
        };
        chrome.runtime.sendMessage(message).catch(e=>{});
        if (id_win != null && id_win > 0) chrome.windows.update(id_win, { state: 'minimized' });
        return Promise.resolve('').catch(e=>{});
    }

    tab = sender.tab.id;
    checkBeforeCreate(msg.request, tab, msg.domain); // ← passes to checkBeforeCreate
    request = msg.request;
    request_id = msg.request_id;
    id_win = 0;
}

// Background bg.js - Line 1276 (Inside checkBeforeCreate flow)
if (data.addKeys) updateAccount(data.username, data.addKeys); // ← if addKeys provided

// Background bg.js - Lines 1085-1120 (Storage sink)
function updateAccount(username, keys) {
    if (mk == null || !keys || !username || username == '') return;
    if (accounts == null) accounts = { list: [], hash: ''};

    let chain = username.substring(0,3).toLowerCase();
    let chain_prefix = Steem.config.networks[chain] ? Steem.config.networks[chain].address_prefix : chain.toUpperCase();
    let is_bts = chain.startsWith('bts') || chain == 'gph' || chain == 'ppy' || chain == 'usc';

    let account = accounts.list.find(e => e.name == username);
    if (account == null) {
        account = { name: username, keys: {} };
        accounts.list.push(account);
    }
    if (keys.active) {
        account.keys.active = keys.active;
        account.keys.activePubkey = chain_prefix+Steem.Auth.wifToPublic(keys.active).substring(3);
    }
    if (!is_bts && keys.posting) {
        account.keys.posting = keys.posting;
        account.keys.postingPubkey = chain_prefix+Steem.Auth.wifToPublic(keys.posting).substring(3);
    }
    if (keys.memo) {
        account.keys.memo = keys.memo;
        account.keys.memoPubkey = chain_prefix+Steem.Auth.wifToPublic(keys.memo).substring(3);
    }

    accounts.list.sort(function(a,b) {
        if (a.name < b.name) return -1;
        if (a.name > b.name) return 1;
        return 0;
    });

    chrome.storage.local.set({
        accounts: encryptJson(accounts, mk) // ← sink: encrypted storage
    });
}

// Background bg.js - Lines 1302-1314 (Response back to attacker)
let message = {
    command: "answerRequest",
    msg: {
        success: true,
        error: null,
        result: pubkeys, // ← only sends back PUBLIC keys, not private keys
        data: data,
        message: "Pubkeys retrieved successfully",
        request_id: request_id
    }
};
chrome.tabs.sendMessage(tab, message).catch(e=>{});
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation. While a malicious webpage can dispatch custom DOM events (`wvHandshake` and `wvRequest`) to trigger the extension to store data in `chrome.storage.local`, the exploitation chain is incomplete for the following reasons:

1. **User Interaction Required**: The `updateAccount` function (line 1276) is only called within the `checkBeforeCreate` flow, which requires user confirmation through a popup dialog (lines 1792-1884, 1869-1884). The extension creates a popup asking the user to confirm adding/updating keys. Without user approval, the storage write never happens.

2. **No Direct Retrieval Path**: When the extension responds to the webpage (lines 1302-1314), it only sends back public keys (`pubkeys`), not the private keys stored in `chrome.storage.local`. The attacker cannot retrieve sensitive encrypted private keys from legitimate users.

3. **Encryption Protection**: All sensitive account data is encrypted with the user's master key (`mk`) before storage (line 1118: `encryptJson(accounts, mk)`). Even if an attacker could poison the storage, they cannot decrypt existing legitimate user data without the master key.

4. **Self-Poisoning Only**: An attacker can only store their own keys (which they already know) after user confirmation. They cannot poison or retrieve other users' encrypted keys from storage.

While the attack vector (DOM event listener) exists and data can flow to storage, the lack of a complete exploitation chain (no retrieval of sensitive data to attacker, user confirmation required, encryption protection) makes this a FALSE POSITIVE according to the methodology. The storage poisoning alone, without the ability to retrieve sensitive data back to the attacker, is not exploitable.
