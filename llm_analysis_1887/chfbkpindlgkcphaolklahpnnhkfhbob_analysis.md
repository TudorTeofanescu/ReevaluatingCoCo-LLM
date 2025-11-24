# CoCo Analysis: chfbkpindlgkcphaolklahpnnhkfhbob

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 3

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (message.lastName)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/chfbkpindlgkcphaolklahpnnhkfhbob/opgen_generated_files/bg.js
Line 1082	                        'lastName': message.lastName,
	message.lastName
```

**Code:**

```javascript
// Background script (bg.js) - External message handler
chrome.runtime.onMessageExternal.addListener(function (message, sender, sendResponse) {
  if (message.type === "loginUser") {
    const formData = new FormData();
    formData.append('userID', message.userID);
    formData.append('userPassword', message.userPassword);

    // Validate credentials against hardcoded backend
    fetch(`${server_url}/server/userLogin.php`, {
      method: 'POST',
      body: formData
    })
    .then(response => response.text())
    .then(data => {
      if (data === 'Login successful!') {
        console.log('user has logged in.')
        chrome.storage.local.set({
          'userID': message.userID,          // ← attacker-controlled (but validated)
          'firstName': message.firstName,    // ← attacker-controlled (but validated)
          'lastName': message.lastName,      // ← attacker-controlled (but validated)
          'userLoggedIn': 'true'
        });
        chrome.runtime.reload();
        sendResponse({ status: 'success', message: 'User logged in successfully on extension.' });
      } else {
        sendResponse({ status: 'error', message: 'Login failed on extension.' });
      }
    })
    .catch(error => {
      console.error('Error:', error);
      sendResponse({ status: 'error', message: 'Login error on extension.' });
    });
    return true;
  }
});

// Storage retrieval - sends to hardcoded backend, not to attacker
chrome.storage.local.get('userID', function (result) {
  userID = result.userID;
  if (userID) {
    getUserGames(userID); // Calls hardcoded backend at server_url
  } else {
    console.log('Scavnj Error: userID not found in local storage');
  }
});

function getUserGames(userID) {
  console.log('userID', userID)
  fetch(`${server_url}/server/getUserActiveGameData.php?userID=${userID}`)
    .then(response => response.json())
    .then(data => {
      console.log('Array of Active Game Data:', data);
      arrayOfActiveGameData = data;
      // Data used internally, not sent back to attacker
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** Data flows to/from hardcoded backend (trusted infrastructure). While external messages from whitelisted domains (*://*.scavnj.com/* per manifest.json) can trigger the flow, the user data is only stored AFTER successful validation against the developer's backend server (`${server_url}/server/userLogin.php`). Subsequently, when storage is retrieved (line 1164), the data is sent back to the same trusted backend server (`${server_url}/server/getUserActiveGameData.php`), not to the attacker. This represents communication with the developer's own infrastructure, which is trusted. Compromising the developer's backend is an infrastructure issue, not an extension vulnerability.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (message.firstName)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/chfbkpindlgkcphaolklahpnnhkfhbob/opgen_generated_files/bg.js
Line 1081	                        'firstName': message.firstName,
	message.firstName
```

**Classification:** FALSE POSITIVE

**Reason:** Same as Sink 1 - data flows to/from hardcoded backend (trusted infrastructure).

---

## Sink 3: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (message.userID)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/chfbkpindlgkcphaolklahpnnhkfhbob/opgen_generated_files/bg.js
Line 1080	                        'userID': message.userID,
	message.userID
```

**Classification:** FALSE POSITIVE

**Reason:** Same as Sink 1 - data flows to/from hardcoded backend (trusted infrastructure).
