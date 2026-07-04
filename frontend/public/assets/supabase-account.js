(function () {
  var config = window.boostAISupabaseConfig || {};
  var messageEl = document.getElementById("message");
  var emailEl = document.getElementById("account-email");
  var idEl = document.getElementById("account-id");
  var signOutBtn = document.getElementById("signout-btn");
  var studyLink = document.getElementById("study-link");
  var localSessionKey = "boostai-local-session";

  function showMessage(type, text) {
    messageEl.className = "message show " + type;
    messageEl.textContent = text;
  }

  function usingPlaceholderConfig() {
    return !config.url || !config.anonKey || config.url.indexOf("YOUR_SUPABASE") !== -1 || config.anonKey.indexOf("YOUR_SUPABASE") !== -1;
  }

  function loadLocalSession() {
    try {
      return JSON.parse(localStorage.getItem(localSessionKey) || "null");
    } catch {
      return null;
    }
  }

  function clearLocalSession() {
    localStorage.removeItem(localSessionKey);
  }

  if (usingPlaceholderConfig()) {
    var localSession = loadLocalSession();

    if (!localSession) {
      emailEl.textContent = "No active static session";
      idEl.textContent = "No active static session";
      showMessage("error", "You are not signed in. Go back to the login page to continue.");
      if (studyLink) studyLink.classList.remove("hidden");
    } else {
      emailEl.textContent = localSession.email || "Unknown";
      idEl.textContent = localSession.id || "Unknown";
      showMessage("info", "Static login mode is active and your local session has loaded.");
      if (studyLink) studyLink.classList.remove("hidden");
    }

    signOutBtn.addEventListener("click", function () {
      clearLocalSession();
      showMessage("info", "Signed out. Redirecting to login…");
      setTimeout(function () {
        window.location.href = "/login.html?mode=login";
      }, 350);
    });

    return;
  }

  var client = window.supabase.createClient(config.url, config.anonKey);

  client.auth.getSession().then(function (result) {
    var session = result.data && result.data.session;

    if (!session || !session.user) {
      emailEl.textContent = "No active session";
      idEl.textContent = "No active session";
      showMessage("error", "You are not signed in. Go back to the login page to continue.");
      if (studyLink) studyLink.classList.remove("hidden");
      return;
    }

    emailEl.textContent = session.user.email || "Unknown";
    idEl.textContent = session.user.id || "Unknown";
    showMessage("info", "Session loaded successfully.");
    if (studyLink) studyLink.classList.remove("hidden");
  });

  signOutBtn.addEventListener("click", async function () {
    var result = await client.auth.signOut();
    if (result.error) {
      showMessage("error", result.error.message || "Could not sign out.");
      return;
    }

    showMessage("info", "Signed out. Redirecting to login…");
    setTimeout(function () {
      window.location.href = "/login.html?mode=login";
    }, 400);
  });
}());
