# Streamlit-dashboard voor AI-nieuwsagent

import streamlit as st
import feedparser
import os
from openai import OpenAI
from datetime import datetime

# Instellingen
st.set_page_config(page_title="AI Nieuwsagent", layout="wide")
st.title("🗞️ AI-Nieuwsagent voor woningcorporaties")

# Initialiseer OpenAI-client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# RSS-feeds
feeds = {
    "NOS": "https://feeds.nos.nl/nosnieuwsalgemeen",
    "Rijksoverheid (woningbouw)": "https://www.rijksoverheid.nl/onderwerpen/woningbouw/rss",
    "Overheid.nl (kamerstukken)": "https://zoek.officielebekendmakingen.nl/rss/kamerstukken.xml",
    "VNG (wonen en bouwen)": "https://www.vng.nl/onderwerpenindex/wonen-en-bouwen/rss.xml",
    "Leidsch Dagblad": "https://www.leidschdagblad.nl/rss",
    "Google News (Wonen NL)": "https://news.google.com/rss/search?q=woningcorporatie+OR+volkshuisvesting+OR+leefbaarheid+OR+verduurzaming+when:7d&hl=nl&gl=NL&ceid=NL:nl",
    "NU.nl": "https://www.nu.nl/rss/Algemeen",
    "AD": "https://www.ad.nl/rss.xml",
    "De Telegraaf": "https://www.telegraaf.nl/rss",
    "The Guardian": "https://www.theguardian.com/world/rss",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "Seeking Alpha": "https://seekingalpha.com/feed.xml",
    "Sleutelstad": "https://sleutelstad.nl/feed/",
    "Gemeente Leiderdorp": "https://www.leiderdorp.nl/rss.xml",
    "Gemeente Voorschoten": "https://www.voorschoten.nl/rss.xml",
    "Gemeente Zoeterwoude": "https://www.zoeterwoude.nl/rss.xml"
}

# Thema's voor filtering
alle_themas = [
    "wereldeconomie", "Europese economie", "Nederlandse economie", "geopolitieke machtsblokken",
    "Kabinetsbeleid", "landelijk beleid over woningcorporaties", "nieuwbouw van woningen",
    "energievoorziening en energietransitie", "leefbaarheid in woonwijken", "welzijn en ouderenzorg",
    "sociaal domein", "lokaal woonbeleid in Voorschoten", "lokaal woonbeleid in Zoeterwoude",
    "lokaal woonbeleid in Leiderdorp", "technologie", "aandelen"
]

def analyseer_bericht(title, summary, link):
    prompt = f"""
Je bent een AI-nieuwsassistent voor een woningcorporatie. Vat het onderstaande nieuwsbericht samen in 2-3 zinnen, gericht op de betekenis voor beleid, wonen en samenwerking.

Label het met:
- Thema (kies uit): {', '.join(alle_themas)}.
- Relevantie voor woningcorporaties: hoog, middel of laag (negeer incidenten zonder beleidswaarde zoals branden of ongelukken)

Voeg alleen bij relevante beleidsonderwerpen (woningcorporaties, nieuwbouw, energie, leefbaarheid, zorg, sociaal beleid) een reflectievraag toe die kan helpen bij beleidsvorming.

Titel: {title}
Samenvatting: {summary}
Bron: {link}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Fout bij samenvatten: {str(e)}"

# Selectie van thema's
gekozen_themas = st.multiselect("Filter op thema", options=alle_themas, default=alle_themas)

# Nieuws verzamelen
artikelen = []

for naam, url in feeds.items():
    feed = feedparser.parse(url)
    for entry in feed.entries[:2]:
        summary = getattr(entry, "summary", "") or getattr(entry, "description", "") or ""
        analyse = analyseer_bericht(entry.title, summary, entry.link)

        thema = "Onbekend"
        relevantie = "laag"

        if "Thema:" in analyse:
            try:
                thema = analyse.split("Thema:")[1].split("\n")[0].strip()
            except:
                pass
        if "Relevantie:" in analyse:
            if "hoog" in analyse.lower():
                relevantie = "hoog"
            elif "middel" in analyse.lower():
                relevantie = "middel"

        if thema in gekozen_themas:
            artikelen.append((relevantie, thema, entry.title, analyse, entry.link))

# Sorteer op relevantie
artikelen = sorted(artikelen, key=lambda x: ["hoog", "middel", "laag"].index(x[0]))

# Toon resultaten
for item in artikelen:
    st.markdown(f"### {item[2]}")
    st.markdown(f"**Thema:** {item[1]}  ")
    st.markdown(f"**Relevantie:** {item[0]}  ")
    st.markdown(item[3])
    st.markdown(f"[Lees verder]({item[4]})")
    st.markdown("---")
