#!/usr/bin/env python3
"""
Haalt Google Scholar-publicatiedata op voor gemonitorde onderzoeksteams.
Output: scholar_data.json

Gebruik:
    pip install scholarly
    python scholar_fetch.py
"""

import json
import re
import time
from datetime import datetime, timezone

try:
    from scholarly import scholarly
except ImportError:
    raise SystemExit("Installeer eerst: pip install scholarly")


# ── Teamdefinities ─────────────────────────────────────────────────────────────
# Voeg hier nieuwe teams toe. 'search' is de naam waarmee Scholar wordt doorzocht.
# Zet minder-productieve leden (docenten, bestuur) in commentaar om snelheid te verhogen.

TEAMS = [
    {
        'id': 'pds', 'label': 'PDS · UU', 'inst': 'Utrecht University',
        'members': [
            {'name': 'Elma Blom',                 'search': 'Elma Blom'},
            {'name': 'Maria de Haan',             'search': 'Maria de Haan'},
            {'name': 'Marian Jongmans',           'search': 'Marian Jongmans'},
            {'name': 'Pauline Slot',              'search': 'Pauline Slot'},
            {'name': 'Eva van de Weijer-Bergsma', 'search': 'Eva van de Weijer-Bergsma'},
            {'name': 'Lex Wijnroks',              'search': 'Lex Wijnroks'},
            {'name': 'Paul Baar',                 'search': 'Paul Baar'},
            {'name': 'Tjitske de Groot',          'search': 'Tjitske de Groot'},
            {'name': 'Hanna Mulder',              'search': 'Hanna Mulder'},
            {'name': 'Ora Oudgenoeg-Paz',         'search': 'Ora Oudgenoeg-Paz'},
            {'name': 'Bodine Romijn',             'search': 'Bodine Romijn'},
            {'name': 'Semiha Bekir',              'search': 'Semiha Bekir'},
            {'name': 'Cathy van Tuijl',           'search': 'Cathy van Tuijl'},
            {'name': 'Sietske van Viersen',       'search': 'Sietske van Viersen'},
            {'name': 'Chiel Volman',              'search': 'Michiel Volman'},
            {'name': 'Marieke de Vries',          'search': 'Marieke de Vries'},
            {'name': 'Pomme van de Weerd',        'search': 'Pomme van de Weerd'},
            {'name': 'Merel van Witteloostuijn',  'search': 'Merel van Witteloostuijn'},
            {'name': 'Paul Leseman',              'search': 'Paul Leseman'},
            {'name': 'Hans van Luit',             'search': 'Hans van Luit'},
            {'name': 'Micha de Winter',           'search': 'Micha de Winter'},
            {'name': 'Eduard Elbers',             'search': 'Eduard Elbers'},
            {'name': 'Arthur Bakker',             'search': 'Arthur Bakker'},
            {'name': 'Ryanne Francot',            'search': 'Ryanne Francot'},
            {'name': 'Ine van Liempd',            'search': 'Ine van Liempd'},
            {'name': 'Sanne Appels',              'search': 'Sanne Appels'},
            {'name': 'Hanneke Hart-Baart',        'search': 'Hanneke Hart-Baart'},
            {'name': 'Matthijs Heijstek',         'search': 'Matthijs Heijstek'},
            {'name': 'Isa Linders',               'search': 'Isa Linders'},
            {'name': 'Lianne Stolte',             'search': 'Lianne Stolte'},
        ],
    },
    {
        'id': 'lei', 'label': 'Ped. Wet. · UL', 'inst': 'Leiden University',
        'members': [
            {'name': 'Lenneke Alink',             'search': 'Lenneke Alink'},
            {'name': 'Peter Bos',                 'search': 'Peter Bos'},
            {'name': 'Christine Espin',           'search': 'Christine Espin'},
            {'name': 'Jean-Louis van Gelder',     'search': 'Jean-Louis van Gelder'},
            {'name': 'Stefanie van Goozen',       'search': 'Stefanie van Goozen'},
            {'name': 'Anne-Laura van Harmelen',   'search': 'Anne-Laura van Harmelen'},
            {'name': 'Maretha de Jonge',          'search': 'Maretha de Jonge'},
            {'name': 'Maaike Kempes',             'search': 'Maaike Kempes'},
            {'name': 'Tim Mainhard',              'search': 'Tim Mainhard'},
            {'name': 'Judi Mesman',               'search': 'Judi Mesman'},
            {'name': 'Marga Sikkema-de Jong',     'search': 'Marga Sikkema-de Jong'},
            {'name': 'Wouter Staal',              'search': 'Wouter Staal'},
            {'name': 'Hanna Swaab',               'search': 'Hanna Swaab'},
            {'name': 'Carlijn Bergwerff',         'search': 'Carlijn Bergwerff'},
            {'name': 'Mitch van Geel',            'search': 'Mitch van Geel'},
            {'name': 'Kristiaan van der Heijden', 'search': 'Kristiaan van der Heijden'},
            {'name': 'Marian Hickendorff',        'search': 'Marian Hickendorff'},
            {'name': 'Dietsje Jolles',            'search': 'Dietsje Jolles'},
            {'name': 'Mariëlle Linting',          'search': 'Marielle Linting'},
            {'name': 'Sophie van Rijn',           'search': 'Sophie van Rijn'},
            {'name': 'Ralph Rippe',               'search': 'Ralph Rippe'},
            {'name': 'Shelley van der Veek',      'search': 'Shelley van der Veek'},
            {'name': 'Harriet Vermeer',           'search': 'Harriet Vermeer'},
            {'name': 'Anja van der Voort',        'search': 'Anja van der Voort'},
            {'name': 'Hinke Endedijk',            'search': 'Hinke Endedijk'},
            {'name': 'Anne Helder',               'search': 'Anne Helder'},
            {'name': 'Stephanus Huijbregts',      'search': 'Stephanus Huijbregts'},
            {'name': 'Linda van Leijenhorst',     'search': 'Linda van Leijenhorst'},
            {'name': 'Suzanne Mol',               'search': 'Suzanne Mol'},
            {'name': 'Rachel Plak',               'search': 'Rachel Plak'},
            {'name': 'Emilie Prast',              'search': 'Emilie Prast'},
            {'name': 'Lenny van Rosmalen',        'search': 'Lenny van Rosmalen'},
            {'name': 'Daisy Smeets',              'search': 'Daisy Smeets'},
            {'name': 'Elise Swart',               'search': 'Elise Swart'},
            {'name': 'Merel van Vliet',           'search': 'Merel van Vliet'},
            {'name': 'Simone Vogelaar',           'search': 'Simone Vogelaar'},
            {'name': 'Nienke Bouw',               'search': 'Nienke Bouw'},
        ],
    },
    {
        'id': 'ou', 'label': 'Onderwijs · OU', 'inst': 'Open Universiteit',
        'members': [
            {'name': 'Jos Claessen',          'search': 'Jos Claessen'},
            {'name': 'Elly de Bruijn',        'search': 'Elly de Bruijn'},
            {'name': 'Gino Camp',             'search': 'Gino Camp'},
            {'name': 'Ellen Rusman',          'search': 'Ellen Rusman'},
            {'name': 'Emmy Vrieling-Teunter', 'search': 'Emmy Vrieling'},
            {'name': 'Lisette Wijnia',        'search': 'Lisette Wijnia'},
            {'name': 'Esther Bakker',         'search': 'Esther Bakker'},
            {'name': 'Leen Catrysse',         'search': 'Leen Catrysse'},
            {'name': 'Arnoud Evers',          'search': 'Arnoud Evers'},
            {'name': 'Maartje Henderikx',     'search': 'Maartje Henderikx'},
            {'name': 'Céleste Meijs',         'search': 'Celeste Meijs'},
            {'name': 'François Molin',        'search': 'Francois Molin'},
            {'name': 'Tamara Schleepen',      'search': 'Tamara Schleepen'},
            {'name': 'Iwan Wopereis',         'search': 'Iwan Wopereis'},
            {'name': 'Giel van Lankveld',     'search': 'Giel van Lankveld'},
        ],
    },
    {
        'id': 'til', 'label': 'TiCeLS · TiU', 'inst': 'Tilburg University',
        'members': [
            {'name': 'Monique van Dijk-Groeneboer', 'search': 'Monique van Dijk-Groeneboer'},
            {'name': 'Tessa Leesen',                'search': 'Tessa Leesen'},
            {'name': 'Marije van Amelsvoort',       'search': 'Marije van Amelsvoort'},
            {'name': 'Siebe Bluijs',                'search': 'Siebe Bluijs'},
            {'name': 'Marijn Gijsen',               'search': 'Marijn Gijsen'},
            {'name': 'Wim Maas',                    'search': 'Wim Maas'},
            {'name': 'Gil Keppens',                 'search': 'Gil Keppens'},
            {'name': 'Janneke van der Loo',         'search': 'Janneke van der Loo'},
        ],
    },
]

PAPERS_PER_AUTHOR = 25   # maximale recente papers per auteur
REQUEST_DELAY    = 4     # seconden tussen zoekopdrachten (beleefd)


# ── Hulpfuncties ───────────────────────────────────────────────────────────────

def norm(s):
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z\s]', '', (s or '').lower())).strip()

def name_match(display, target):
    d     = norm(display)
    words = [w for w in norm(target).split() if len(w) > 2]
    return bool(words) and all(w in d for w in words)

def search_author(search_name, institution, retries=3):
    """Zoek een auteur op Scholar. Geeft author-dict terug of None."""
    query = f'{search_name} {institution}'
    for attempt in range(retries):
        try:
            for candidate in scholarly.search_author(query):
                if name_match(candidate.get('name', ''), search_name):
                    return candidate
            return None  # geen match gevonden
        except Exception as e:
            wait = 10 * (attempt + 1)
            print(f"    poging {attempt + 1} mislukt ({e}), wacht {wait}s …")
            time.sleep(wait)
    return None

def fill_author(author):
    """Haal volledige profieldata inclusief publicatielijst op."""
    try:
        return scholarly.fill(author, sections=['basics', 'indices', 'publications'])
    except Exception as e:
        print(f"    fill mislukt: {e}")
        return author

def extract_papers(filled_author, member_name):
    """Zet Scholar-publicaties om naar ons JSON-formaat."""
    pubs = filled_author.get('publications', [])
    pubs_sorted = sorted(
        pubs,
        key=lambda p: int(p.get('bib', {}).get('pub_year') or 0),
        reverse=True,
    )
    papers = []
    for pub in pubs_sorted[:PAPERS_PER_AUTHOR]:
        bib   = pub.get('bib', {})
        title = bib.get('title', '').strip()
        if not title:
            continue
        papers.append({
            'title':       title,
            'year':        bib.get('pub_year', ''),
            'venue':       bib.get('venue', '') or bib.get('journal', ''),
            'cited_by':    pub.get('num_citations', 0),
            'url':         pub.get('pub_url', '')
                           or f"https://scholar.google.com/scholar?q={title}",
            'team_author': member_name,
        })
    return papers


# ── Hoofdprogramma ─────────────────────────────────────────────────────────────

def main():
    output = {
        'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'teams':     {},
    }

    for team in TEAMS:
        print(f"\n{'=' * 55}")
        print(f"  {team['label']}  ({team['inst']})")
        print(f"{'=' * 55}")

        team_papers   = []
        seen_titles   = set()
        members_found = 0
        member_log    = []

        for m in team['members']:
            print(f"  → {m['name']:<35}", end=' ', flush=True)

            author = search_author(m['search'], team['inst'])
            if not author:
                print('niet gevonden')
                member_log.append({'name': m['name'], 'found': False})
                time.sleep(REQUEST_DELAY)
                continue

            filled  = fill_author(author)
            papers  = extract_papers(filled, m['name'])
            h_index = filled.get('hindex')
            cites   = filled.get('citedby')
            members_found += 1

            member_log.append({
                'name':       m['name'],
                'found':      True,
                'scholar_id': filled.get('scholar_id', ''),
                'h_index':    h_index,
                'cited_by':   cites,
            })

            new_papers = 0
            for p in papers:
                if p['title'] not in seen_titles:
                    seen_titles.add(p['title'])
                    team_papers.append(p)
                    new_papers += 1

            print(f"h={h_index or '?'}  citaties={cites or '?'}  +{new_papers} papers")
            time.sleep(REQUEST_DELAY)

        team_papers.sort(key=lambda p: str(p.get('year', '0')).zfill(4), reverse=True)

        output['teams'][team['id']] = {
            'label':         team['label'],
            'members_found': members_found,
            'members_total': len(team['members']),
            'members':       member_log,
            'papers':        team_papers,
        }

        print(f"\n  ✓ {members_found}/{len(team['members'])} gevonden · "
              f"{len(team_papers)} unieke papers")

    with open('scholar_data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    totaal_auteurs = sum(t['members_found'] for t in output['teams'].values())
    totaal_papers  = sum(len(t['papers'])   for t in output['teams'].values())
    print(f"\n✓ scholar_data.json geschreven "
          f"({totaal_auteurs} auteurs · {totaal_papers} papers · "
          f"{output['generated']})")


if __name__ == '__main__':
    main()
