# Apex redirect

`lincolnplumbingandrooter.com` (no www) can't point at Railway: Railway needs a
CNAME for a custom domain, a CNAME is illegal at a zone apex, and GoDaddy DNS
has no ALIAS/ANAME/flattening record to work around it. GoDaddy's own Domain
Forwarding is what's there now, and it only handles the bare root — it 301s
`/` to `https://www.lincolnplumbingandrooter.com` while **dropping both the path
and the query string**, so:

    https://lincolnplumbingandrooter.com/            -> 301 to www root  (loses ?gclid)
    https://lincolnplumbingandrooter.com/hydrojetting -> 404 from awselb

This folder is a two-file site whose only job is to redirect the apex properly,
preserving path and query. It goes on any host that will serve an apex domain
from a plain A record — Netlify is the easy one, and free.

## Deploying it

1. Netlify → Add new site → **Deploy manually**, and drag this folder in.
2. Site configuration → Domain management → **Add a domain**:
   `lincolnplumbingandrooter.com` (apex only — leave `www` alone, that's Railway).
3. Netlify shows the A record to use for an apex (currently `75.2.60.5`). Note it.
4. In GoDaddy DNS for the domain:
   - **Delete** the two forwarding `A` records on `@`
     (`15.197.225.128`, `3.33.251.168`), and remove the Domain Forwarding entry
     itself, or GoDaddy will put them back.
   - **Add** `A  @  <the IP Netlify gave you>`.
   - Leave `CNAME  www  fcctb4p3.up.railway.app` exactly as it is.
5. Wait for Netlify to issue the certificate (a few minutes once DNS resolves).

## Verifying

    curl -sI https://lincolnplumbingandrooter.com/hydrojetting/ | grep -i '^HTTP/\|^location'
    # want: 301 -> https://www.lincolnplumbingandrooter.com/hydrojetting/

    curl -sI 'https://lincolnplumbingandrooter.com/?gclid=abc123' | grep -i '^location'
    # want: the gclid still on the end

`index.html` is only a fallback for the unlikely case that `_redirects` isn't
applied; the `301!` rule handles every real request.
