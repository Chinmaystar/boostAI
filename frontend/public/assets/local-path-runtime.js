(function () {
  if (window.location.protocol !== "file:") {
    return;
  }

  var base = window.__boostAiLocalBase || "./";
  var routePattern = /^\/(school|uni|university|study|practice|auth|account|library)(?:\/?|\/index\.html)?(?:[?#].*)?$/i;
  var assetPattern = /^\/(?:assets|fonts|Images|practice-bank)\//;
  var singleFilePattern = /^\/(?:favicon\.(?:png|webp)|logo\.(?:png|svg|webp))$/i;

  function isExternal(url) {
    return /^(?:[a-z][a-z0-9+.-]*:|\/\/|#|mailto:|tel:|data:|javascript:)/i.test(url);
  }

  function resolve(url) {
    if (!url || typeof url !== "string" || isExternal(url)) {
      return url;
    }

    if (url === "/") {
      return base + "index.html";
    }

    if (url.charAt(0) !== "/") {
      return url;
    }

    if (assetPattern.test(url) || singleFilePattern.test(url)) {
      return base + url.replace(/^\/+/, "");
    }

    if (routePattern.test(url)) {
      return base + url.replace(/^\/+/, "").replace(/\/?$/, "/index.html");
    }

    return base + url.replace(/^\/+/, "");
  }

  function resolveSrcset(srcset) {
    if (!srcset || typeof srcset !== "string") {
      return srcset;
    }

    return srcset.split(",").map(function (part) {
      var trimmed = part.trim();
      if (!trimmed) {
        return trimmed;
      }

      var firstSpace = trimmed.indexOf(" ");
      if (firstSpace === -1) {
        return resolve(trimmed);
      }

      return resolve(trimmed.slice(0, firstSpace)) + trimmed.slice(firstSpace);
    }).join(", ");
  }

  function patchProperty(proto, name, formatter) {
    if (!proto) {
      return;
    }

    var descriptor = Object.getOwnPropertyDescriptor(proto, name);
    if (!descriptor || typeof descriptor.set !== "function") {
      return;
    }

    Object.defineProperty(proto, name, {
      configurable: true,
      enumerable: descriptor.enumerable,
      get: descriptor.get,
      set: function (value) {
        descriptor.set.call(this, formatter(value));
      }
    });
  }

  function rewriteElement(el) {
    ["href", "src", "poster"].forEach(function (name) {
      var value = el.getAttribute && el.getAttribute(name);
      if (value && value.charAt(0) === "/") {
        el.setAttribute(name, resolve(value));
      }
    });

    var srcset = el.getAttribute && el.getAttribute("srcset");
    if (srcset) {
      el.setAttribute("srcset", resolveSrcset(srcset));
    }
  }

  function rewriteTree(root) {
    var selector = "[href],[src],[poster],[srcset]";
    if (root.matches && root.matches(selector)) {
      rewriteElement(root);
    }

    Array.prototype.forEach.call(root.querySelectorAll ? root.querySelectorAll(selector) : [], rewriteElement);
  }

  window.__boostAiResolveLocalPath = resolve;
  window.__boostAiResolveLocalSrcset = resolveSrcset;

  var nativeSetAttribute = Element.prototype.setAttribute;
  Element.prototype.setAttribute = function (name, value) {
    if (typeof value === "string") {
      if (name === "href" || name === "src" || name === "poster") {
        value = resolve(value);
      } else if (name === "srcset") {
        value = resolveSrcset(value);
      }
    }

    return nativeSetAttribute.call(this, name, value);
  };

  patchProperty(typeof HTMLAnchorElement !== "undefined" && HTMLAnchorElement.prototype, "href", resolve);
  patchProperty(typeof HTMLLinkElement !== "undefined" && HTMLLinkElement.prototype, "href", resolve);
  patchProperty(typeof HTMLImageElement !== "undefined" && HTMLImageElement.prototype, "src", resolve);
  patchProperty(typeof HTMLImageElement !== "undefined" && HTMLImageElement.prototype, "srcset", resolveSrcset);
  patchProperty(typeof HTMLScriptElement !== "undefined" && HTMLScriptElement.prototype, "src", resolve);
  patchProperty(typeof HTMLIFrameElement !== "undefined" && HTMLIFrameElement.prototype, "src", resolve);
  patchProperty(typeof HTMLSourceElement !== "undefined" && HTMLSourceElement.prototype, "src", resolve);

  if (window.fetch) {
    var nativeFetch = window.fetch;
    window.fetch = function (input, init) {
      if (typeof input === "string") {
        input = resolve(input);
      } else if (input && typeof input.url === "string" && input.url.charAt(0) === "/") {
        input = new Request(resolve(input.url), input);
      }

      return nativeFetch.call(this, input, init);
    };
  }

  var nativePushState = history.pushState;
  history.pushState = function (state, title, url) {
    if (typeof url === "string") {
      url = resolve(url);
    }

    return nativePushState.call(this, state, title, url);
  };

  var nativeReplaceState = history.replaceState;
  history.replaceState = function (state, title, url) {
    if (typeof url === "string") {
      url = resolve(url);
    }

    return nativeReplaceState.call(this, state, title, url);
  };

  document.addEventListener("DOMContentLoaded", function () {
    rewriteTree(document);
  });
}());
