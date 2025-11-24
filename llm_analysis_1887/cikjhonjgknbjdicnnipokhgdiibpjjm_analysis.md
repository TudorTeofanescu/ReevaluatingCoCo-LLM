# CoCo Analysis: cikjhonjgknbjdicnnipokhgdiibpjjm

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → jQuery_ajax_settings_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cikjhonjgknbjdicnnipokhgdiibpjjm/opgen_generated_files/cs_0.js
Line 1465 - window.addEventListener("message", function (event)
Line 1471 - if (event.data.type && (event.data.type === "FROM_PAGE"))
Line 1472 - consoleLog("Content script received message: " + event.data.text)

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cikjhonjgknbjdicnnipokhgdiibpjjm/opgen_generated_files/bg.js
Line 1160 - 'url': `/save_event/${kwargs['id']}/${token}/`
Line 987 - config['url'] = api_url + config['url']

**Code:**

```javascript
// Content Script (cs_0.js)
// Line 1452: Hardcoded backend URL
const api_url = 'https://carpebrutus.com';

// Line 1465-1492: window.postMessage listener
window.addEventListener("message", function (event) {
    if (event.source !== window)
        return

    if (event.data.type && (event.data.type === "FROM_PAGE")) {
        consoleLog("Content script received message: " + event.data.text)
        chrome.storage.sync.get("brutus_extension_user", (items) => {
            api_request({
                'request': {
                    'service': 'save_event',
                    'kwargs': {'id': event.data.text, 'token': items['brutus_extension_user']['token']},  // ← attacker-controlled 'id'
                },
                'response': {
                    'callback': function (xhr, kwargs) {
                        // ...
                    },
                }
            });
        })
    }
});

// Line 606: Content script sends message to background
chrome.extension.sendMessage({
    'message_id': message_id,
    'from': 'brutus_content',
    'subject': 'api_call',
    'service': config.request.service,  // 'save_event'
    'kwargs': config.request.kwargs,    // {'id': attacker-controlled, 'token': user_token}
}, (message_response) => { /* ... */ });

// Background Script (bg.js)
// Line 966: Hardcoded backend URL
const api_url = 'https://carpebrutus.com'

// Line 1153-1163: save_event function
const save_event = (kwargs) => {
    const token = kwargs['token'];
    if (token === undefined) {
        return {}
    }
    return {
        'method': 'get',
        'url': `/save_event/${kwargs['id']}/${token}/`,  // ← attacker-controlled 'id' in path
    }
};

// Line 979-1023: api_request function
const api_request = (message_id, service, user, random_user_uuid, kwargs, msg_callback) => {
    let config;
    if (typeof services[service] == 'function') {
        config = services[service](kwargs);  // Calls save_event(kwargs)
    }

    config['url'] = api_url + config['url'];  // Prepends hardcoded 'https://carpebrutus.com'
    // Result: https://carpebrutus.com/save_event/{attacker-controlled-id}/{token}/

    $.ajax(config).done(function (data) {
        // Makes request to hardcoded backend
    })
}
```

**Classification:** FALSE POSITIVE

**Reason:** Although attacker-controlled data from `window.postMessage` flows into the jQuery ajax URL, the request is sent TO the hardcoded developer backend URL (`https://carpebrutus.com`). The attacker can only influence the path parameter (`id`) in the request to the developer's own trusted infrastructure. This is not exploitable because the data is sent to the developer's backend server, not to an attacker-controlled destination. Compromising the developer's backend is an infrastructure security issue, not an extension vulnerability.
