(function () {
  var config = window.boostAISupabaseConfig || {};
  var params = new URLSearchParams(window.location.search);
  var mode = params.get("mode") || "login";
  var returnTo = params.get("returnTo") || "/study/";
  var messageEl = document.getElementById("message");
  var tabs = Array.prototype.slice.call(document.querySelectorAll(".tab"));
  var form = document.getElementById("auth-form");
  var emailInput = document.getElementById("email");
  var passwordInput = document.getElementById("password");
  var confirmInput = document.getElementById("confirm-password");
  var passwordWrap = document.getElementById("password-wrap");
  var confirmWrap = document.getElementById("confirm-wrap");
  var helperCopy = document.getElementById("helper-copy");
  var submitBtn = document.getElementById("submit-btn");
  var accountBtn = document.getElementById("account-btn");
  var localUsersKey = "boostai-local-users";
  var localSessionKey = "boostai-local-session";

  function showMessage(type, text) {
    messageEl.className = "message show " + type;
    messageEl.textContent = text;
  }

  function clearMessage() {
    messageEl.className = "message";
    messageEl.textContent = "";
  }

  function nextLocation() {
    return returnTo && returnTo !== "/auth/" ? returnTo : "/study/";
  }

  function applyMode(nextMode) {
    mode = nextMode;
    tabs.forEach(function (tab) {
      tab.classList.toggle("active", tab.dataset.mode === mode);
    });

    confirmWrap.classList.toggle("hidden", mode !== "signup");
    passwordWrap.classList.toggle("hidden", mode === "reset");
    passwordInput.required = mode !== "reset";
    confirmInput.required = mode === "signup";

    if (mode === "login") {
      submitBtn.textContent = "Log in";
      helperCopy.textContent = "Use your existing account to continue to your BoostAI workspace.";
    } else if (mode === "signup") {
      submitBtn.textContent = "Create account";
      helperCopy.textContent = "Create a new account with email and password.";
    } else {
      submitBtn.textContent = "Send reset email";
      helperCopy.textContent = "Enter your email and we will send a local reset message for this static build.";
    }
  }

  function saveUsers(users) {
    localStorage.setItem(localUsersKey, JSON.stringify(users));
  }

  function loadUsers() {
    try {
      return JSON.parse(localStorage.getItem(localUsersKey) || "[]");
    } catch {
      return [];
    }
  }

  function saveSession(session) {
    localStorage.setItem(localSessionKey, JSON.stringify(session));
  }

  function loadSession() {
    try {
      return JSON.parse(localStorage.getItem(localSessionKey) || "null");
    } catch {
      return null;
    }
  }

  function buildLocalUser(email, password) {
    return {
      id: "local-" + Date.now() + "-" + Math.random().toString(36).slice(2, 8),
      email: email,
      password: password,
      createdAt: new Date().toISOString()
    };
  }

  function activateAccountButton() {
    accountBtn.classList.remove("hidden");
    accountBtn.textContent = "Open account";
    accountBtn.href = "/account/";
  }

  function usingPlaceholderConfig() {
    return !config.url || !config.anonKey || config.url.indexOf("YOUR_SUPABASE") !== -1 || config.anonKey.indexOf("YOUR_SUPABASE") !== -1;
  }

  tabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
      clearMessage();
      applyMode(tab.dataset.mode);
      var nextParams = new URLSearchParams();
      nextParams.set("mode", tab.dataset.mode);
      if (returnTo) nextParams.set("returnTo", returnTo);
      history.replaceState({}, "", "/login.html?" + nextParams.toString());
    });
  });

  accountBtn.addEventListener("click", function () {
    window.location.href = accountBtn.getAttribute("href") || nextLocation();
  });

  if (usingPlaceholderConfig()) {
    var currentSession = loadSession();
    showMessage("info", "Static login mode is active. This build works without Supabase until you add real keys.");
    if (currentSession) {
      activateAccountButton();
    }

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      clearMessage();

      var email = emailInput.value.trim().toLowerCase();
      var password = passwordInput.value;
      var confirmPassword = confirmInput.value;
      var users = loadUsers();

      if (!email) {
        showMessage("error", "Enter your email.");
        return;
      }

      if (mode === "signup") {
        if (password.length < 6) {
          showMessage("error", "Use at least 6 characters for the password.");
          return;
        }

        if (password !== confirmPassword) {
          showMessage("error", "Passwords do not match.");
          return;
        }

        if (users.some(function (user) { return user.email === email; })) {
          showMessage("error", "That email already has an account. Try logging in instead.");
          return;
        }

        var newUser = buildLocalUser(email, password);
        users.push(newUser);
        saveUsers(users);
        saveSession({ id: newUser.id, email: newUser.email, mode: "local" });
        activateAccountButton();
        showMessage("success", "Account created. Redirecting…");
        setTimeout(function () {
          window.location.href = nextLocation();
        }, 400);
        return;
      }

      if (mode === "reset") {
        var existing = users.find(function (user) { return user.email === email; });
        if (!existing) {
          showMessage("error", "No local account was found for that email.");
          return;
        }
        showMessage("success", "Reset requested. In static mode, log in with your existing password or create a new test account.");
        return;
      }

      var matched = users.find(function (user) {
        return user.email === email && user.password === password;
      });

      if (!matched) {
        showMessage("error", "Email or password did not match.");
        return;
      }

      saveSession({ id: matched.id, email: matched.email, mode: "local" });
      activateAccountButton();
      showMessage("success", "Logged in successfully. Redirecting…");
      setTimeout(function () {
        window.location.href = nextLocation();
      }, 400);
    });

    applyMode(mode);
    return;
  }

  var client = window.supabase.createClient(config.url, config.anonKey);

  client.auth.getSession().then(function (result) {
    if (result.data && result.data.session) {
      activateAccountButton();
      showMessage("success", "You are already signed in. You can continue to your account page.");
    }
  });

  form.addEventListener("submit", async function (event) {
    event.preventDefault();
    clearMessage();

    var email = emailInput.value.trim();
    var password = passwordInput.value;
    var confirmPassword = confirmInput.value;

    try {
      if (mode === "signup") {
        if (password !== confirmPassword) {
          showMessage("error", "Passwords do not match.");
          return;
        }

        var signUpResult = await client.auth.signUp({
          email: email,
          password: password
        });

        if (signUpResult.error) throw signUpResult.error;
        if (signUpResult.data && signUpResult.data.session) {
          showMessage("success", "Account created. Redirecting…");
          setTimeout(function () {
            window.location.href = nextLocation();
          }, 500);
          return;
        }

        showMessage("success", "Account created. Check your email if your project requires email confirmation.");
        activateAccountButton();
        return;
      }

      if (mode === "reset") {
        var resetResult = await client.auth.resetPasswordForEmail(email, {
          redirectTo: window.location.origin + "/login.html?mode=login"
        });

        if (resetResult.error) throw resetResult.error;
        showMessage("success", "Password reset email sent.");
        return;
      }

      var signInResult = await client.auth.signInWithPassword({
        email: email,
        password: password
      });

      if (signInResult.error) throw signInResult.error;
      showMessage("success", "Logged in successfully. Redirecting…");
      setTimeout(function () {
        window.location.href = nextLocation();
      }, 500);
    } catch (error) {
      showMessage("error", error.message || "Something went wrong.");
    }
  });

  applyMode(mode);
}());
