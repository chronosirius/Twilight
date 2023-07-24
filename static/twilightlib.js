try {
    __TWILIGHTAPP
} catch (err) {

const __TWILIGHTAPP = {
    $ORIGINALS_: {
        setTimeout: setTimeout.bind(window),
        setInterval: setInterval.bind(window),
        clearTimeout: clearTimeout.bind(window),
        clearInterval: clearInterval.bind(window),
        fetch: fetch.bind(window)
    },
    $COUNTERS: {
        Timeouts_: [],
        Intervals_: []
    },
    $CACHES: {},
    setHTML: function(selector, html) {
        document.querySelector(selector).innerHTML = html
    },
    GLOBAL_ABORT: new AbortController(),
    COOKIES: Object.fromEntries(new URLSearchParams(document.cookie.replace(/; /g, "&"))),
    SESSION_STORE: {},
    COMMAND_QUEUE: []
}

var setTimeout = function(callback, wait, ...forwardArguments) {
    let p = __TWILIGHTAPP.$ORIGINALS_.setTimeout(callback, wait, ...forwardArguments)
    __TWILIGHTAPP.$COUNTERS.Timeouts_.push(p)
    return p
}
var clearTimeout = function(timeoutId) {
    __TWILIGHTAPP.$ORIGINALS_.clearTimeout(timeoutId)
    __TWILIGHTAPP.$COUNTERS.Timeouts_.splice(__TWILIGHTAPP.$COUNTERS.Timeouts_.indexOf(timeoutId), 1)
}

var setInterval = function(callback, wait, ...forwardArguments) {
    let p = __TWILIGHTAPP.$ORIGINALS_.setInterval(callback, wait, ...forwardArguments)
    __TWILIGHTAPP.$COUNTERS.Intervals_.push(p)
    return p
}
var clearTimeout = function(intervalId) {
    __TWILIGHTAPP.$ORIGINALS_.clearInterval(intervalId)
    __TWILIGHTAPP.$COUNTERS.Intervals_.splice(__TWILIGHTAPP.$COUNTERS.Intervals_.indexOf(intervalId), 1)
}

var fetch = function(url, settings = {}) {
    if (!settings.signal) {
        settings.signal = __TWILIGHTAPP.GLOBAL_ABORT.signal
    }
    return __TWILIGHTAPP.$ORIGINALS_.fetch(url, settings)
}

function redirect(path, nopush) {
    fetch(path).then((res) => {return res.text()}).then((text) => {
        let htmlDoc = (new DOMParser()).parseFromString(text, 'text/html')
        let head = document.createRange().createContextualFragment(htmlDoc.head.innerHTML)
        let body = document.createRange().createContextualFragment(htmlDoc.body.innerHTML)
        console.log(document.head)
        let headEl = document.createElement('head')
        let bodyEl = document.createElement('body')
        headEl.append(head.cloneNode(true))
        bodyEl.append(body.cloneNode(true))
        document.querySelector('html').replaceChild(headEl.cloneNode(true), document.head)
        document.querySelector('html').replaceChild(bodyEl.cloneNode(true), document.body)
        if (!nopush) {
            history.pushState({
                'referer': window.location.toString(),
                'page': 1
            }, '', path)
        }
    })
}
window.addEventListener('popstate', function(ev) {
    console.log(ev)
    p = window.dispatchEvent(new Event('leave'))
    if (!p) {
        if (confirm('Are you sure you want to leave this page?')) {
            redirect(window.location.toString(), true)
        }
    } else {
        redirect(window.location.toString(), true)
    }
})
function getElementSelector(elem) {
    var tagName = elem.tagName, id = elem.id, className = elem.className, parentElement = elem.parentElement;
    var str = '';
    if (id !== '' && id.match(/^[a-z].*/)) {
        str += "#".concat(id);
        return str;
    }
    str = tagName;
    if (className) {
        str += '.' + className.replace(/(^\s)/gm, '').replace(/(\s{2,})/gm, ' ')
            .split(/\s/).join('.');
    }
    var needNthPart = function (el) {
        var sib = el.previousElementSibling;
        if (!el.className) {
            return true;
        }
        while (sib) {
            if (el.className !== sib.className) {
                return false;
            }
            sib = sib.previousElementSibling;
        }
        return false;
    };
    var getNthPart = function (el) {
        var childIndex = 1;
        var sib = el.previousElementSibling;
        while (sib) {
            childIndex++;
            sib = sib.previousElementSibling;
        }
        return ":nth-child(".concat(childIndex, ")");
    };
    if (needNthPart(elem)) {
        str += getNthPart(elem);
    }
    if (!parentElement) {
        return str;
    }
    return "".concat(elemToSelector(parentElement), " > ").concat(str);
}

}