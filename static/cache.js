/// <reference no-default-lib="true"/>
/// <reference lib="esnext" />
/// <reference lib="webworker" /> 
/**@type {ServiceWorkerGlobalScope} self */

async function fastget({req}) {
    cache_res = await self.caches.match(req)
    if (cache_res) {
        if (req.url === cache_res.url) {
            return cache_res;
        }
    }

    try {
        const network_res = await fetch(req)
        if (network_res.status == 502) {
            if (req.headers.get('Accept').includes('application/json')) {
                return new Response('{"error": "SERVICE_DOWN", "http_code": 502}', {
                    status: 502,
                    headers: {
                        "Content-Type": "application/json"
                    }
                })
            } else {
                return new Response(`
                    <html>
                        <head>
                            <title>Down | Twilight</title>
                            <style>
                                * {
                                    color: white;
                                    font-family: sans-serif;
                                }
                                body {
                                    background-color: #343434;
                                }
                            </style>
                        </head>
                        <body>
                            <center>
                                <h1>Down</h1>
                                <p>It seems Twilight is down. Please wait for it to come up.</p>
                            </center>
                        </body>
                    </html>`, {
                    status: 502,
                    headers: {
                        "Content-Type": "text/html"
                    }
                })
            }
        }
        if (new URL(req.url).pathname.startsWith('/cdn/') || new URL(req.url).pathname.startsWith('/static/') && new URL(req.url).pathname != "/static/cache.js") {
            cache = await self.caches.open('cdn_cache')
            cache.put(req, network_res.clone())
            console.log(`Cached from CDN (${req.url}).`)
        } else if (new URL(req.url).hostname == 'fonts.gstatic.com' || new URL(req.url).hostname == 'fonts.googleapis.com') {
            cache = await self.caches.open('cdn_cache')
            cache.put(req, network_res.clone())
            console.log(`Cached from font-store (${req.url}).`)
        } else {
            console.log(`Refusing to cache, not from CDN (${req.url}).`)
        }
        return network_res;
    } catch (err) {
        console.error(err)
        if (req.headers.get('Accept').includes('application/json')) {
            return new Response('{"error": "NO_NETWORK", "http_code": 408}', {
                status: 408,
                headers: {
                    "Content-Type": "application/json"
                }
            })
        } else {
            return new Response(`
                <html>
                    <head>
                        <title>Offline | Twilight</title>
                        <style>
                            * {
                                color: white;
                                font-family: sans-serif;
                            }
                            body {
                                background-color: #343434;
                            }
                        </style>
                    </head>
                    <body>
                        <center>
                            <h1>Offline</h1>
                            <p>It seems you are offline. Please reconnect to the internet to continue.</p>
                        </center>
                    </body>
                </html>`, {
                status: 408,
                headers: {
                    "Content-Type": "text/html"
                }
            })
        }
    }
}

self.addEventListener('install', ev => {
    ev.waitUntil(self.caches.open('basecache').then(cache => {
        cache.addAll([
            '/favicon.ico',
            '/',
            '/cdn/__default_user__.webp',
            '/cdn/__default_server__.webp',
            '/static/ctxmenu.js'
        ]).then(() => {console.log('Installed!')})
    }))
    ev.waitUntil(self.skipWaiting())
})

self.addEventListener('activate', ev => {
    ev.waitUntil(self.clients.claim())
})

self.addEventListener('fetch', ev => {
    r = fastget({
        req: ev.request
    })
    ev.respondWith(r)
    // updateCaches(ev.request)
})