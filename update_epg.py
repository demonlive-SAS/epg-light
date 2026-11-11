import os
import gzip
import re
import xml.etree.ElementTree as ET
import requests

try:
    from lxml import etree as lxml_etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False

# Settings
NAME = "light"
# Get URL from GitHub Secret
M3U_URL = os.getenv("M3U_URL")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "epgs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# We only define the .gz path to stay under GitHub's 100MB limit
OUTPUT_FILE_GZ = os.path.join(OUTPUT_DIR, f"{NAME}-epg.xml.gz")

URLS = [
    'https://epgshare01.online/epgshare01/epg_ripper_US2.xml.gz',
    'https://epgshare01.online/epgshare01/epg_ripper_US_LOCALS1.xml.gz',
    'https://epgshare01.online/epgshare01/epg_ripper_CA2.xml.gz',
    'https://epgshare01.online/epgshare01/epg_ripper_UK1.xml.gz',
    'https://epgshare01.online/epgshare01/epg_ripper_MX1.xml.gz',
    'https://epgshare01.online/epgshare01/epg_ripper_AU1.xml.gz',
    'https://epgshare01.online/epgshare01/epg_ripper_US_SPORTS1.xml.gz',
    'https://epgshare01.online/epgshare01/epg_ripper_FANDUEL1.xml.gz',
    'https://epgshare01.online/epgshare01/epg_ripper_DUMMY_CHANNELS.xml.gz',
    'https://epgshare01.online/epgshare01/epg_ripper_TBNPLUS1.xml.gz',
    'https://github.com/demonlive-SAS/RakutenTV-UK/raw/refs/heads/main/playlist.m3u',
    'http://mains.services/xmltv.php?username=tmo247line&password=65s4d64vgfdfbae4',
    'https://github.com/demonlive-SAS/buddy_airy/raw/refs/heads/main/airy_channels.xml',
    'https://github.com/matthuisman/i.mjh.nz/raw/refs/heads/master/SamsungTVPlus/all.xml.gz',
    'https://github.com/demonlive-SAS/samstvplus/raw/refs/heads/main/output/samsung_tvplus.xml',
    'https://github.com/demonlive-SAS/buddy_tcl_playlist/raw/refs/heads/main/tcl_epg.xml',
    'https://github.com/matthuisman/i.mjh.nz/raw/refs/heads/master/nzau/epg.xml.gz',
    'https://raw.githubusercontent.com/BuddyChewChew/localnow-playlist-generator/refs/heads/main/epg.xml',
    'https://github.com/matthuisman/i.mjh.nz/raw/master/Plex/all.xml.gz',
    'https://raw.githubusercontent.com/BuddyChewChew/dummy-epg-project/refs/heads/main/epg.xml',
    'https://github.com/matthuisman/i.mjh.nz/raw/master/Roku/all.xml',
    'https://epg.pw/api/epg.xml?lang=en&timezone=VVMvRWFzdGVybg%3D%3D&date=20260405&channel_id=464981',
    'https://github.com/BuddyChewChew/xumo-playlist-generator/raw/refs/heads/main/playlists/xumo_epg.xml.gz',
    'https://raw.githubusercontent.com/matthuisman/i.mjh.nz/refs/heads/master/PlutoTV/all.xml',
    'https://github.com/demonlive-SAS/fast-bally/raw/refs/heads/main/ballys.xml',
    'https://iptv-epg.org/files/epg-al.xml',
    'https://iptv-epg.org/files/epg-am.xml',
    'https://iptv-epg.org/files/epg-au.xml',
    'https://iptv-epg.org/files/epg-at.xml',
    'https://iptv-epg.org/files/epg-bs.xml',
    'https://iptv-epg.org/files/epg-by.xml',
    'https://iptv-epg.org/files/epg-be.xml',
    'https://iptv-epg.org/files/epg-bo.xml',
    'https://iptv-epg.org/files/epg-ba.xml',
    'https://iptv-epg.org/files/epg-br.xml',
    'https://iptv-epg.org/files/epg-bg.xml',
    'https://iptv-epg.org/files/epg-ca.xml',
    'https://iptv-epg.org/files/epg-co.xml',
    'https://iptv-epg.org/files/epg-cr.xml',
    'https://iptv-epg.org/files/epg-hr.xml',
    'https://iptv-epg.org/files/epg-cz.xml',
    'https://iptv-epg.org/files/epg-dk.xml',
    'https://iptv-epg.org/files/epg-do.xml',
    'https://iptv-epg.org/files/epg-sv.xml',
    'https://iptv-epg.org/files/epg-fi.xml',
    'https://iptv-epg.org/files/epg-fr.xml',
    'https://iptv-epg.org/files/epg-ge.xml',
    'https://iptv-epg.org/files/epg-de.xml',
    'https://iptv-epg.org/files/epg-gh.xml',
    'https://iptv-epg.org/files/epg-gr.xml',
    'https://iptv-epg.org/files/epg-gt.xml',
    'https://iptv-epg.org/files/epg-hn.xml',
    'https://iptv-epg.org/files/epg-hk.xml',
    'https://iptv-epg.org/files/epg-hu.xml',
    'https://iptv-epg.org/files/epg-is.xml',
    'https://iptv-epg.org/files/epg-in.xml',
    'https://iptv-epg.org/files/epg-id.xml',
    'https://iptv-epg.org/files/epg-il.xml',
    'https://iptv-epg.org/files/epg-it.xml',
    'https://iptv-epg.org/files/epg-jm.xml',
    'https://iptv-epg.org/files/epg-jp.xml',
    'https://iptv-epg.org/files/epg-lv.xml',
    'https://iptv-epg.org/files/epg-lt.xml',
    'https://iptv-epg.org/files/epg-lu.xml',
    'https://iptv-epg.org/files/epg-mk.xml',
    'https://iptv-epg.org/files/epg-my.xml',
    'https://iptv-epg.org/files/epg-mt.xml',
    'https://iptv-epg.org/files/epg-mx.xml',
    'https://iptv-epg.org/files/epg-me.xml',
    'https://iptv-epg.org/files/epg-nl.xml',
    'https://iptv-epg.org/files/epg-nz.xml',
    'https://iptv-epg.org/files/epg-ni.xml',
    'https://iptv-epg.org/files/epg-ng.xml',
    'https://iptv-epg.org/files/epg-no.xml',
    'https://iptv-epg.org/files/epg-pa.xml',
    'https://iptv-epg.org/files/epg-py.xml',
    'https://iptv-epg.org/files/epg-pl.xml',
    'https://iptv-epg.org/files/epg-pt.xml',
    'https://iptv-epg.org/files/epg-ro.xml',
    'https://iptv-epg.org/files/epg-ru.xml',
    'https://iptv-epg.org/files/epg-rs.xml',
    'https://iptv-epg.org/files/epg-sg.xml',
    'https://iptv-epg.org/files/epg-za.xml',
    'https://iptv-epg.org/files/epg-es.xml',
    'https://iptv-epg.org/files/epg-se.xml',
    'https://iptv-epg.org/files/epg-ch.xml',
    'https://iptv-epg.org/files/epg-tw.xml',
    'https://iptv-epg.org/files/epg-th.xml',
    'https://iptv-epg.org/files/epg-tt.xml',
    'https://iptv-epg.org/files/epg-tr.xml',
    'https://iptv-epg.org/files/epg-ug.xml',
    'https://iptv-epg.org/files/epg-gb.xml',
    'https://iptv-epg.org/files/epg-us.xml',
    'https://iptv-epg.org/files/epg-ve.xml',
    'https://iptv-epg.org/files/epg-zw.xml',
]

# Remove exact duplicate URLs while preserving order
URLS = list(dict.fromkeys(URLS))


def get_tvg_ids_from_remote_m3u():
    """Downloads M3U from GitFlic and extracts tvg-id values."""
    tvg_ids = set()
    if not M3U_URL:
        print("CRITICAL: No M3U_URL secret found.")
        return None

    print("Downloading M3U from GitFlic...")
    try:
        response = requests.get(M3U_URL, timeout=30)
        if response.status_code != 200:
            print(f"Failed to download M3U: {response.status_code}")
            return None

        # Extract tvg-id="value"
        pattern = re.compile(r'tvg-id="([^"]+)"')
        matches = pattern.findall(response.text)
        for val in matches:
            tvg_ids.add(val)

        print(f"Successfully mapped {len(tvg_ids)} channels from your playlist.")
        return tvg_ids
    except Exception as e:
        print(f"Error fetching M3U: {e}")
        return None


def sanitize_xml_bytes(content):
    """Strip bytes that are illegal in XML 1.0 but keep valid whitespace."""
    return re.sub(rb'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', b'', content)


def parse_xml(content, url):
    """Try strict stdlib parse first, fall back to lxml recovery, then sanitize + retry."""
    # 1. Fast path: strict stdlib parse
    try:
        return ET.fromstring(content)
    except ET.ParseError:
        pass

    # 2. lxml with recover=True (handles most real-world malformed EPGs)
    if HAS_LXML:
        try:
            root_lxml = lxml_etree.fromstring(content, parser=lxml_etree.XMLParser(recover=True))
            # Convert lxml element back to stdlib ET so the rest of the script is unchanged
            return ET.fromstring(lxml_etree.tostring(root_lxml))
        except Exception:
            pass

    # 3. Strip illegal control characters and retry stdlib
    try:
        return ET.fromstring(sanitize_xml_bytes(content))
    except ET.ParseError as e:
        print(f"  ! Error: {e}")
        return None


def fetch_and_parse(url):
    try:
        print(f"Fetching EPG: {url.split('/')[-1]}")
        response = requests.get(url, timeout=60)
        if response.status_code != 200:
            print(f"  ! HTTP {response.status_code}")
            return None
        content = response.content
        # Decompress if gzip (by extension or by magic bytes)
        if url.endswith('.gz') or content[:2] == b'\x1f\x8b':
            content = gzip.decompress(content)
        return parse_xml(content, url)
    except Exception as e:
        print(f"  ! Error: {e}")
        return None


def main():
    valid_ids = get_tvg_ids_from_remote_m3u()

    # SAFETY CHECK: Stop if M3U fails to prevent pulling ~400MB of data to GitHub
    if not valid_ids:
        print("Stopping process: M3U filter is required to stay under GitHub file size limits.")
        return

    master_root = ET.Element('tv', {"generator-info-name": "BuddyChewChew-Light-GZ-Only"})

    # Track what's already added so overlapping sources don't create duplicates
    seen_channels = set()
    seen_programmes = set()

    for url in URLS:
        epg_data = fetch_and_parse(url)
        if epg_data is None:
            continue

        for channel in epg_data.findall('channel'):
            cid = channel.get('id')
            if cid in valid_ids and cid not in seen_channels:
                seen_channels.add(cid)
                master_root.append(channel)

        for prog in epg_data.findall('programme'):
            ch = prog.get('channel')
            if ch not in valid_ids:
                continue

            key = (ch, prog.get('start'), prog.get('stop'))
            if key in seen_programmes:
                continue
            seen_programmes.add(key)

            title = prog.find('title')
            if title is not None and title.text in ['NHL Hockey', 'Live: NFL Football']:
                sub = prog.find('sub-title')
                if sub is not None and sub.text:
                    title.text = f"{title.text} {sub.text}"
            master_root.append(prog)

    # Write ONLY the .gz file to save space and stay under 100MB
    print(f"Saving compressed EPG to {OUTPUT_FILE_GZ}...")
    tree = ET.ElementTree(master_root)
    with gzip.open(OUTPUT_FILE_GZ, 'wb') as f:
        tree.write(f, encoding='utf-8', xml_declaration=True)

    print("M3U-Filtered EPG (.gz only) generation complete.")


if __name__ == "__main__":
    main()
