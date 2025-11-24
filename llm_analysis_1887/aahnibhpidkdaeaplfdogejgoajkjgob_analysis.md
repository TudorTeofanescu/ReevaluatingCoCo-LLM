# CoCo Analysis: aahnibhpidkdaeaplfdogejgoajkjgob

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** Multiple fetch_resource_sink detections

---

## Sink: bg_chrome_runtime_MessageExternal → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/aahnibhpidkdaeaplfdogejgoajkjgob/opgen_generated_files/bg.js
Line 1179: `if (message.url && message.url.startsWith('magnet:'))`
Line 1055: `'?action=add-url&download_dir=0&token=' + token + '&s=' + encodeURI(link)`
Line 1063: `return fetch(settings.host + params, {...})`

**Code:**

```javascript
// Background script - External message handler
chrome.runtime.onMessageExternal.addListener(
  (message, sender, sendResponse) => {
    switch (message.type) {
      case 'ADD_TORRENT':
        if (message.url && message.url.startsWith('magnet:'))
          withSettings((settings) => {
            addTorrents(settings, message.url, message.folder) // ← attacker-controlled
          })
        else
          withSettings((settings) => {
            downloadLink(settings, message.url, message.folder) // ← attacker-controlled
          })
        break
    }
  }
)

function addTorrents(settings, link, where) {
  GetTokenNew(settings, function (token, cookie) {
    let params =
      '?action=add-url&download_dir=0&token=' + token + '&s=' + encodeURI(link) // ← attacker data in params

    if (where !== ROOT_FOLDER) params += '&path=' + where // ← attacker-controlled folder

    const myHeaders = new Headers({
      Authorization: 'Basic ' + btoa(settings.user + ':' + settings.password),
    })

    return fetch(settings.host + params, { // ← fetch to hardcoded backend (settings.host)
      method: 'GET',
      headers: myHeaders,
    })
  })
}

function downloadLink(settings, link, where) {
  return fetch(link, { // ← fetch to attacker URL but goes to user's backend
    method: 'GET',
    headers: myHeaders,
  })
}
```

**Classification:** FALSE POSITIVE

**Reason:** The fetch requests go to hardcoded backend URLs (`settings.host`) controlled by the user's own uTorrent/BitTorrent server. The `settings.host` value comes from the extension's options page (user configuration), not attacker input. While an external attacker can trigger the flow via `chrome.runtime.onMessageExternal` and control the URL/folder parameters, the destination of the fetch request is the user's trusted backend infrastructure (their local uTorrent server). According to the methodology: "Hardcoded backend URLs remain trusted infrastructure" - data sent TO/FROM developer's (or user's) own backend servers is FALSE POSITIVE because compromising that infrastructure is a separate issue from extension vulnerabilities.
