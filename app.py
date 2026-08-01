import os
import streamlit as st
from datetime import date, timedelta
import holidays as holidays_lib

from daten import (
    lade_config, speichere_config,
    lade_plaene, speichere_plaene, gesamteinsaetze,
    lade_entwurf, speichere_entwurf,
    str_zu_datum, DATEN_VERZEICHNIS,
)
from planer import generiere_plan, berechne_einsaetze, validiere_plan, WOCHENTAGE
from pdf_export import erstelle_pdf

BUNDESLAENDER = {
    "BB": "Brandenburg", "BE": "Berlin", "BW": "Baden-Württemberg",
    "BY": "Bayern", "HB": "Bremen", "HE": "Hessen", "HH": "Hamburg",
    "MV": "Mecklenburg-Vorpommern", "NI": "Niedersachsen",
    "NW": "Nordrhein-Westfalen", "RP": "Rheinland-Pfalz",
    "SH": "Schleswig-Holstein", "SL": "Saarland", "SN": "Sachsen",
    "ST": "Sachsen-Anhalt", "TH": "Thüringen",
}

FEIERTAG_DE = {
    "New Year's Day": "Neujahr",
    "Good Friday": "Karfreitag",
    "Easter Sunday": "Ostersonntag",
    "Easter Monday": "Ostermontag",
    "Labour Day": "Tag der Arbeit",
    "Labor Day": "Tag der Arbeit",
    "Ascension Day": "Christi Himmelfahrt",
    "Whit Sunday": "Pfingstsonntag",
    "Whit Monday": "Pfingstmontag",
    "Corpus Christi": "Fronleichnam",
    "Assumption Day": "Mariä Himmelfahrt",
    "German Unity Day": "Tag der Deutschen Einheit",
    "Reformation Day": "Reformationstag",
    "All Saints' Day": "Allerheiligen",
    "Christmas Day": "1. Weihnachtstag",
    "Second Day of Christmas": "2. Weihnachtstag",
    "Epiphany": "Heilige Drei Könige",
    "World Children's Day": "Weltkindertag",
    "International Women's Day": "Internationaler Frauentag",
    "Liberation Day": "Tag der Befreiung",
    "Peace Festival": "Augsburger Friedensfest",
}


def _feiertag_name_de(name: str) -> str:
    return FEIERTAG_DE.get(name, name)


def _letzter_tag_nach_3_monaten(start: date) -> date:
    month = start.month + 3
    year = start.year + (month - 1) // 12
    month = ((month - 1) % 12) + 1
    if month == 12:
        return date(year, 12, 31)
    return date(year, month + 1, 1) - timedelta(days=1)


def render_plan_html(plan: list, config: dict) -> str:
    gerichte = config.get("gerichte", {})
    plan_index = {e["datum"]: e for e in plan}
    erster = date.fromisoformat(plan[0]["datum"])
    letzter = date.fromisoformat(plan[-1]["datum"])
    montag_start = erster - timedelta(days=erster.weekday())
    freitag_ende = letzter + timedelta(days=(4 - letzter.weekday()))
    wochen: list[list[date]] = []
    d = montag_start
    while d <= freitag_ende:
        wochen.append([d + timedelta(days=i) for i in range(5)])
        d += timedelta(days=7)

    wochentage_lang = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
    kopf_zellen = ""
    for i, tag in enumerate(wochentage_lang):
        gericht = gerichte.get(str(i), "")
        kopf_zellen += f'<th>{tag}<br><span class="gericht">{gericht}</span></th>'

    zeilen_html = ""
    for w_idx, woche in enumerate(wochen):
        kw = woche[0].isocalendar()[1]
        zellen = ""
        for tag in woche:
            datum_str = tag.isoformat()
            eintrag = plan_index.get(datum_str)
            if eintrag is None:
                zellen += '<td class="leer"></td>'
            elif eintrag.get("schliesszeit_name"):
                sz_anzeige = eintrag["schliesszeit_name"]
                zellen += (
                    f'<td><span class="datum">{tag.strftime("%d.%m.%Y")}</span>'
                    f'<span class="sonder">{sz_anzeige}</span></td>'
                )
            else:
                kind_name = eintrag.get("kind", "")
                anzeige = kind_name if kind_name else "–"
                manuell = ' <span class="manuell">✏</span>' if eintrag.get("manuell_geaendert") else ""
                zellen += (
                    f'<td><span class="datum">{tag.strftime("%d.%m.%Y")}</span>'
                    f'<span class="name">{anzeige}{manuell}</span></td>'
                )
        zeilenfarbe = "#F0F4F0" if w_idx % 2 == 0 else "#FFFFFF"
        zeilen_html += (
            f'<tr style="background-color:{zeilenfarbe};">'
            f'<td class="kw-zelle">KW {kw}</td>{zellen}</tr>'
        )

    return f"""<style>
  .kochplan {{ width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 14px; }}
  .kochplan th {{
    background-color: #4A7C59; color: white; padding: 8px 10px;
    text-align: center; border: 1px solid #3a6347;
  }}
  .kochplan th .gericht {{ font-size: 0.78em; font-weight: normal; color: #CCEEDD; display: block; margin-top: 2px; }}
  .kochplan td {{ padding: 6px 10px; vertical-align: top; border: 1px solid #CCCCCC; min-width: 110px; }}
  .kochplan td.kw-zelle {{
    background-color: #E8F0EA !important; font-weight: bold; color: #000000;
    text-align: center; vertical-align: middle; white-space: nowrap;
  }}
  .kochplan td.leer {{ background-color: #F8F8F8; }}
  .kochplan .datum {{ font-size: 0.75em; color: #999999; display: block; margin-bottom: 2px; }}
  .kochplan .name {{ font-weight: bold; display: block; color: #000000; }}
  .kochplan .sonder {{ font-style: italic; color: #AAAAAA; display: block; }}
  .kochplan .manuell {{ color: #E07020; font-style: normal; font-size: 0.85em; }}
</style>
<table class="kochplan">
  <thead><tr><th>Woche</th>{kopf_zellen}</tr></thead>
  <tbody>{zeilen_html}</tbody>
</table>"""


st.set_page_config(page_title="Kindergarten Kochplan", page_icon="🍲", layout="wide")
st.title("Kindergarten Kochplan")


# --- Session State initialisieren ---
if "config" not in st.session_state:
    st.session_state.config = lade_config()
if "plan" not in st.session_state:
    entwurf = lade_entwurf()
    if entwurf:
        st.session_state.plan = entwurf["plan"]
        st.session_state.plan_zustand = "entwurf"
        st.session_state.entwurf_von = date.fromisoformat(entwurf["von"])
        st.session_state.entwurf_bis = date.fromisoformat(entwurf["bis"])
    else:
        st.session_state.plan = []
if "plan_zustand" not in st.session_state:
    st.session_state.plan_zustand = "keiner"
if "plaene" not in st.session_state:
    st.session_state.plaene = lade_plaene()
if "detail_plan_id" not in st.session_state:
    st.session_state.detail_plan_id = None

config = st.session_state.config


# === SEITENLEISTE: Konfiguration ===
with st.sidebar:
    st.header("Konfiguration")

    # --- Schließzeiten ---
    with st.expander("Schließzeiten", expanded=False):
        schliesszeiten: list[dict] = config["einstellungen"].get("schliesszeiten", [])

        bundesland_optionen = list(BUNDESLAENDER.keys())
        bundesland_aktuell = config["einstellungen"].get("bundesland", "HE")
        bundesland_idx = bundesland_optionen.index(bundesland_aktuell) if bundesland_aktuell in bundesland_optionen else 0
        bl = st.selectbox(
            "Bundesland",
            options=bundesland_optionen,
            index=bundesland_idx,
            format_func=lambda k: f"{k} – {BUNDESLAENDER[k]}",
            key="bundesland_select",
        )
        config["einstellungen"]["bundesland"] = bl

        feiertag_jahr = st.number_input(
            "Jahr für Feiertage", min_value=2020, max_value=2040,
            value=date.today().year, step=1, key="feiertag_jahr",
        )
        if st.button("Feiertage generieren", key="btn_feiertage_gen"):
            feiertage_dict = holidays_lib.Germany(subdiv=bl, years=int(feiertag_jahr))
            bestehende_namen = {(sz["von"], sz["name"]) for sz in schliesszeiten}
            neu = 0
            for ft_datum, ft_name in sorted(feiertage_dict.items()):
                ft_name = _feiertag_name_de(ft_name)
                key = (ft_datum.isoformat(), ft_name)
                if key not in bestehende_namen:
                    schliesszeiten.append({
                        "name": ft_name,
                        "von": ft_datum.isoformat(),
                        "bis": ft_datum.isoformat(),
                        "automatisch": True,
                    })
                    neu += 1
            config["einstellungen"]["schliesszeiten"] = schliesszeiten
            st.success(f"{neu} Feiertage für {bl} {int(feiertag_jahr)} hinzugefügt.")

        st.divider()

        with st.form("neue_schliesszeit", clear_on_submit=True):
            sz_name = st.text_input("Bezeichnung (z.B. Sommerferien)")
            sz_von = st.date_input("Von", key="sz_von")
            sz_bis = st.date_input("Bis", key="sz_bis")
            if st.form_submit_button("Hinzufügen"):
                if sz_name:
                    schliesszeiten.append({
                        "name": sz_name,
                        "von": sz_von.isoformat(),
                        "bis": sz_bis.isoformat(),
                        "automatisch": False,
                    })
                    config["einstellungen"]["schliesszeiten"] = schliesszeiten
                    st.success(f'"{sz_name}" hinzugefügt.')

        if schliesszeiten:
            st.write("**Eingetragene Schließzeiten:**")
            for i, sz in enumerate(sorted(schliesszeiten, key=lambda x: x["von"])):
                zeitraum = sz["von"] if sz["von"] == sz["bis"] else f"{sz['von']} – {sz['bis']}"
                auto_label = " 🗓" if sz.get("automatisch") else ""
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{sz['name']}**{auto_label}  \n{zeitraum}")
                if c2.button("✕", key=f"del_sz_{i}_{sz['von']}"):
                    schliesszeiten.remove(sz)
                    config["einstellungen"]["schliesszeiten"] = schliesszeiten
                    st.rerun()

    # --- Gerichte ---
    with st.expander("Gerichte pro Wochentag", expanded=False):
        gerichte = config.get("gerichte", {})
        for i, tag in enumerate(WOCHENTAGE):
            gerichte[str(i)] = st.text_input(
                tag, value=gerichte.get(str(i), ""), key=f"gericht_{i}"
            )
        config["gerichte"] = gerichte

    # --- Kinder ---
    with st.expander("Kinder verwalten", expanded=False):
        kinder = config.get("kinder", [])

        with st.form("neues_kind", clear_on_submit=True):
            st.subheader("Kind hinzufügen")
            neues_kind_name = st.text_input("Name")
            neuer_vorstand = st.checkbox("Vorstandsmitglied (wird halb so oft eingeplant)")
            neuer_wochentage = st.multiselect(
                "Erlaubte Wochentage (leer = alle)",
                options=list(range(5)),
                format_func=lambda x: WOCHENTAGE[x],
            )
            if st.form_submit_button("Hinzufügen"):
                if neues_kind_name and not any(k["name"] == neues_kind_name for k in kinder):
                    kinder.append({
                        "name": neues_kind_name,
                        "ist_vorstand": neuer_vorstand,
                        "erlaubte_wochentage": neuer_wochentage,
                        "sperrzeiten": [],
                    })
                    config["kinder"] = kinder
                    st.success(f"{neues_kind_name} hinzugefügt.")

        if kinder:
            st.divider()
            for idx, kind in enumerate(kinder):
                with st.expander(kind["name"], expanded=False):
                    kind["ist_vorstand"] = st.checkbox(
                        "Vorstandsmitglied", value=kind.get("ist_vorstand", False), key=f"vorstand_{idx}"
                    )
                    kind["erlaubte_wochentage"] = st.multiselect(
                        "Erlaubte Wochentage (leer = alle)",
                        options=list(range(5)),
                        default=kind.get("erlaubte_wochentage", []),
                        format_func=lambda x: WOCHENTAGE[x],
                        key=f"wochentage_{idx}",
                    )
                    sperrzeiten = kind.get("sperrzeiten", [])
                    st.write("**Sperrzeiten**")
                    sp_col1, sp_col2 = st.columns(2)
                    sp_von = sp_col1.date_input("Von", key=f"sperre_von_{idx}")
                    sp_bis = sp_col2.date_input("Bis", key=f"sperre_bis_{idx}")
                    if st.button("Sperrzeit eintragen", key=f"btn_sperre_{idx}"):
                        sperrzeiten.append({"von": sp_von.isoformat(), "bis": sp_bis.isoformat()})
                        kind["sperrzeiten"] = sperrzeiten
                    if sperrzeiten:
                        st.write("Sperrzeiten:")
                        for sp in sorted(sperrzeiten, key=lambda x: x["von"] if isinstance(x, dict) else x):
                            sc1, sc2 = st.columns([3, 1])
                            if isinstance(sp, dict):
                                zeitraum = sp["von"] if sp["von"] == sp["bis"] else f"{sp['von']} – {sp['bis']}"
                            else:
                                zeitraum = sp
                            sc1.write(zeitraum)
                            if sc2.button("✕", key=f"del_sp_{idx}_{sp if isinstance(sp, str) else sp['von']}"):
                                sperrzeiten.remove(sp)
                                kind["sperrzeiten"] = sperrzeiten
                    if st.button("Kind entfernen", key=f"del_kind_{idx}"):
                        kinder.pop(idx)
                        config["kinder"] = kinder
                        st.rerun()

        config["kinder"] = kinder

    # --- Logo ---
    with st.expander("Logo (PDF)", expanded=False):
        logo_pfad = config["einstellungen"].get("logo_pfad", "")
        if logo_pfad and os.path.exists(logo_pfad):
            st.image(logo_pfad, width=120)
        hochgeladen = st.file_uploader("Logo hochladen (PNG/JPG)", type=["png", "jpg", "jpeg"], key="logo_upload")
        if hochgeladen:
            logo_ziel = os.path.join(DATEN_VERZEICHNIS, "logo" + os.path.splitext(hochgeladen.name)[1])
            with open(logo_ziel, "wb") as f:
                f.write(hochgeladen.read())
            config["einstellungen"]["logo_pfad"] = logo_ziel
            st.success("Logo gespeichert.")
            st.rerun()
        if logo_pfad and os.path.exists(logo_pfad):
            if st.button("Logo entfernen", key="btn_logo_entfernen"):
                os.remove(logo_pfad)
                config["einstellungen"]["logo_pfad"] = ""
                st.rerun()

    st.divider()
    if st.button("Konfiguration speichern", type="primary"):
        speichere_config(config)
        st.success("Gespeichert.")


# === HAUPTBEREICH ===

tab_plan, tab_historie = st.tabs(["Plan", "Historie"])

with tab_plan:
    # Defaults für Planungszeitraum
    n_plaene = len(st.session_state.plaene)
    if st.session_state.plaene:
        letzter_plan_bis = date.fromisoformat(st.session_state.plaene[-1]["bis"])
        min_start = letzter_plan_bis + timedelta(days=1)
    else:
        min_start = date.today()

    default_start = min_start
    default_end = _letzter_tag_nach_3_monaten(default_start)

    if st.session_state.plan_zustand == "entwurf" and "entwurf_von" in st.session_state:
        default_start = st.session_state.entwurf_von
        default_end = st.session_state.entwurf_bis
        min_start = min(min_start, default_start)

    # Datum-Eingaben und Aktions-Buttons
    col_von, col_bis, col_gen, col_pdf = st.columns([2, 2, 2, 2])

    with col_von:
        plan_von = st.date_input(
            "Von",
            value=default_start,
            min_value=min_start,
            key=f"plan_von_{n_plaene}",
        )

    with col_bis:
        plan_bis = st.date_input(
            "Bis",
            value=default_end,
            min_value=min_start,
            key=f"plan_bis_{n_plaene}",
        )

    with col_gen:
        st.write("")  # vertical alignment
        ist_entwurf = st.session_state.plan_zustand == "entwurf"
        gen_label = "Plan generieren"
        if st.button(
            gen_label,
            type="primary",
            disabled=ist_entwurf,
            help="Erst den aktuellen Entwurf publizieren oder verwerfen." if ist_entwurf else None,
        ):
            gesamt = gesamteinsaetze(st.session_state.plaene)
            st.session_state.plan = generiere_plan(config, gesamt, plan_von, plan_bis)
            st.session_state.plan_zustand = "entwurf"
            st.session_state.entwurf_von = plan_von
            st.session_state.entwurf_bis = plan_bis
            speichere_entwurf({
                "von": plan_von.isoformat(),
                "bis": plan_bis.isoformat(),
                "plan": st.session_state.plan,
            })
            st.success(f"Plan {plan_von.strftime('%d.%m.%Y')} – {plan_bis.strftime('%d.%m.%Y')} generiert.")

    plan = st.session_state.plan

    if plan:
        warnungen = validiere_plan(plan, config)
        if warnungen:
            with st.expander(f"⚠️ {len(warnungen)} Warnung(en)", expanded=True):
                for w in warnungen:
                    st.warning(w["meldung"])

        with col_pdf:
            einsaetze = berechne_einsaetze(plan)
            pdf_bytes = erstelle_pdf(plan, config, einsaetze)
            st.write("")  # vertical alignment
            st.download_button(
                "PDF herunterladen",
                data=pdf_bytes,
                file_name="kochplan.pdf",
                mime="application/pdf",
            )

        # Status-Badge und Publish-Button
        status_col, pub_col, discard_col = st.columns([4, 2, 2])
        if st.session_state.plan_zustand == "entwurf":
            status_col.markdown(
                '<span style="background:#F0A500;color:white;padding:3px 10px;border-radius:4px;font-size:0.85em;">Entwurf</span>',
                unsafe_allow_html=True,
            )

        with pub_col:
            if st.button("Plan publizieren", type="primary"):
                from datetime import datetime as _dt
                plan_id = f"{plan_von.isoformat()}_{plan_bis.isoformat()}_{_dt.now().strftime('%Y%m%dT%H%M%S')}"
                st.session_state.plaene.append({
                    "id": plan_id,
                    "von": plan_von.isoformat(),
                    "bis": plan_bis.isoformat(),
                    "publiziert_am": _dt.now().isoformat(timespec="seconds"),
                    "eintraege": st.session_state.plan,
                })
                speichere_plaene(st.session_state.plaene)
                speichere_entwurf(None)
                st.session_state.plan = []
                st.session_state.plan_zustand = "keiner"
                st.success("Plan publiziert.")
                st.rerun()

        with discard_col:
            if st.button("Entwurf verwerfen"):
                speichere_entwurf(None)
                st.session_state.plan = []
                st.session_state.plan_zustand = "keiner"
                st.rerun()

        # Plan-Ansicht
        st.markdown(render_plan_html(plan, config), unsafe_allow_html=True)

        # Statistik
        st.divider()
        einsaetze_aktuell = berechne_einsaetze(plan)
        gesamt_historisch = gesamteinsaetze(st.session_state.plaene)

        col_stat_titel, col_stat_toggle = st.columns([3, 1])
        col_stat_titel.subheader("Einsätze")
        ansicht = col_stat_toggle.radio(
            "Ansicht", ["Tabelle", "Diagramm"], horizontal=True, label_visibility="collapsed"
        )

        statistik_zeilen = []
        for kind in config["kinder"]:
            name = kind["name"]
            aktuell = einsaetze_aktuell.get(name, 0)
            gesamt = gesamt_historisch.get(name, 0) + aktuell
            vorstand = "Ja" if kind.get("ist_vorstand") else "Nein"
            statistik_zeilen.append({
                "Kind": name,
                "Aktueller Plan": aktuell,
                "Gesamt (inkl. Historie)": gesamt,
                "Vorstand": vorstand,
            })

        if statistik_zeilen:
            if ansicht == "Tabelle":
                st.table(statistik_zeilen)
            else:
                import pandas as pd
                import altair as alt

                spalten_optionen = ["Aktueller Plan", "Gesamt (inkl. Historie)"]
                ausgewaehlte_spalten = st.multiselect(
                    "Angezeigte Spalten",
                    options=spalten_optionen,
                    default=spalten_optionen,
                    key="chart_spalten",
                )
                if ausgewaehlte_spalten:
                    df = pd.DataFrame([
                        {"Kind": z["Kind"], "Kategorie": sp, "Einsätze": z[sp]}
                        for z in statistik_zeilen
                        for sp in ausgewaehlte_spalten
                    ])
                    chart = (
                        alt.Chart(df)
                        .mark_bar()
                        .encode(
                            x=alt.X("Kind:N", title="Kind", axis=alt.Axis(labelAngle=0)),
                            xOffset=alt.XOffset("Kategorie:N"),
                            y=alt.Y("Einsätze:Q", title="Einsätze"),
                            color=alt.Color("Kategorie:N", title=""),
                            tooltip=["Kind", "Kategorie", "Einsätze"],
                        )
                        .properties(height=300)
                    )
                    st.altair_chart(chart, use_container_width=True)

        # Manuelle Bearbeitung
        st.divider()
        kinder_namen = [""] + [k["name"] for k in config["kinder"]]
        with st.expander("Plan manuell bearbeiten", expanded=False):
            for idx, eintrag in enumerate(plan):
                if eintrag.get("schliesszeit_name"):
                    continue
                d = date.fromisoformat(eintrag["datum"])
                cols = st.columns([2, 2, 3, 3, 1])
                cols[0].write(d.strftime("%d.%m.%Y"))
                cols[1].write(eintrag["wochentag_name"])
                cols[2].write(eintrag["gericht"])
                aktuelles_kind = eintrag.get("kind", "")
                neues_kind = cols[3].selectbox(
                    "Kind",
                    options=kinder_namen,
                    index=kinder_namen.index(aktuelles_kind) if aktuelles_kind in kinder_namen else 0,
                    key=f"select_{idx}",
                    label_visibility="collapsed",
                )
                if neues_kind != aktuelles_kind:
                    plan[idx]["kind"] = neues_kind
                    plan[idx]["manuell_geaendert"] = True
                    speichere_entwurf({
                        "von": st.session_state.entwurf_von.isoformat(),
                        "bis": st.session_state.entwurf_bis.isoformat(),
                        "plan": plan,
                    })
                if eintrag.get("manuell_geaendert"):
                    cols[4].markdown("✏️")


with tab_historie:
    st.header("Publizierte Pläne")
    plaene = st.session_state.plaene

    if not plaene:
        st.info("Noch keine publizierten Pläne vorhanden.")
    else:
        for plan_eintrag in reversed(plaene):
            pid = plan_eintrag["id"]
            von_str = date.fromisoformat(plan_eintrag["von"]).strftime("%d.%m.%Y")
            bis_str = date.fromisoformat(plan_eintrag["bis"]).strftime("%d.%m.%Y")
            pub_str = plan_eintrag["publiziert_am"].replace("T", " ")

            col_von_h, col_bis_h, col_pub_h, col_det, col_pdf_h, col_del = st.columns([2, 2, 3, 1, 1, 1])
            col_von_h.write(f"**Von:** {von_str}")
            col_bis_h.write(f"**Bis:** {bis_str}")
            col_pub_h.write(f"**Publiziert:** {pub_str}")

            if col_det.button("Details", key=f"det_{pid}"):
                if st.session_state.detail_plan_id == pid:
                    st.session_state.detail_plan_id = None
                else:
                    st.session_state.detail_plan_id = pid

            eintraege = plan_eintrag["eintraege"]
            pdf_bytes_h = erstelle_pdf(eintraege, config, berechne_einsaetze(eintraege))
            col_pdf_h.download_button(
                "PDF",
                data=pdf_bytes_h,
                file_name=f"kochplan_{plan_eintrag['von']}_{plan_eintrag['bis']}.pdf",
                mime="application/pdf",
                key=f"pdf_{pid}",
            )

            if col_del.button("Löschen", key=f"del_{pid}"):
                st.session_state.plaene = [p for p in plaene if p["id"] != pid]
                speichere_plaene(st.session_state.plaene)
                if st.session_state.detail_plan_id == pid:
                    st.session_state.detail_plan_id = None
                st.rerun()

            if st.session_state.detail_plan_id == pid:
                st.markdown(render_plan_html(plan_eintrag["eintraege"], config), unsafe_allow_html=True)

            st.divider()

        # Gesamtübersicht
        st.subheader("Gesamteinsätze")
        gesamt = gesamteinsaetze(plaene)
        if gesamt:
            gesamt_zeilen = [
                {"Kind": name, "Gesamteinsätze": anzahl}
                for name, anzahl in sorted(gesamt.items(), key=lambda x: -x[1])
            ]
            st.table(gesamt_zeilen)
        else:
            st.info("Keine Einsätze in publizierten Plänen.")
