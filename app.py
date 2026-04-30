import streamlit as st
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import calendar

from daten import lade_config, speichere_config, lade_historie, speichere_historie, str_zu_datum
from planer import generiere_plan, berechne_einsaetze, validiere_plan, WOCHENTAGE, elternteil_zu_kinder
from pdf_export import erstelle_pdf

st.set_page_config(page_title="Kindergarten Kochplan", page_icon="🍲", layout="wide")
st.title("Kindergarten Kochplan")


# --- Session State initialisieren ---
if "config" not in st.session_state:
    st.session_state.config = lade_config()
if "plan" not in st.session_state:
    st.session_state.plan = []
if "historie" not in st.session_state:
    st.session_state.historie = lade_historie()


config = st.session_state.config


# === SEITENLEISTE: Konfiguration ===
with st.sidebar:
    st.header("Konfiguration")

    # --- Einstellungen ---
    with st.expander("Planungszeitraum", expanded=False):
        planungsmonate = st.number_input(
            "Monate", min_value=1, max_value=12,
            value=config["einstellungen"].get("planungsmonate", 3),
            key="planungsmonate"
        )
        startdatum = st.date_input(
            "Startdatum",
            value=str_zu_datum(config["einstellungen"].get("startdatum", date.today().isoformat())),
            key="startdatum"
        )
        config["einstellungen"]["planungsmonate"] = planungsmonate
        config["einstellungen"]["startdatum"] = startdatum.isoformat()

    # --- Feiertage ---
    with st.expander("Feiertage (werden übersprungen)", expanded=False):
        feiertage_str = config["einstellungen"].get("feiertage", [])
        neuer_feiertag = st.date_input("Datum hinzufügen", key="neuer_feiertag")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Hinzufügen", key="btn_feiertag_add"):
                if neuer_feiertag.isoformat() not in feiertage_str:
                    feiertage_str.append(neuer_feiertag.isoformat())
                    config["einstellungen"]["feiertage"] = feiertage_str
        if feiertage_str:
            st.write("Eingetragene Tage:")
            for ft in sorted(feiertage_str):
                c1, c2 = st.columns([3, 1])
                c1.write(ft)
                if c2.button("✕", key=f"del_ft_{ft}"):
                    feiertage_str.remove(ft)
                    config["einstellungen"]["feiertage"] = feiertage_str

    # --- Schließtage ---
    with st.expander("Schließtage (erscheinen im Plan)", expanded=False):
        schliesztage_str = config["einstellungen"].get("schliesztage", [])
        neuer_schliesztag = st.date_input("Datum hinzufügen", key="neuer_schliesztag")
        if st.button("Hinzufügen", key="btn_schliesztag_add"):
            if neuer_schliesztag.isoformat() not in schliesztage_str:
                schliesztage_str.append(neuer_schliesztag.isoformat())
                config["einstellungen"]["schliesztage"] = schliesztage_str
        if schliesztage_str:
            st.write("Eingetragene Schließtage:")
            for st_tag in sorted(schliesztage_str):
                c1, c2 = st.columns([3, 1])
                c1.write(st_tag)
                if c2.button("✕", key=f"del_sz_{st_tag}"):
                    schliesztage_str.remove(st_tag)
                    config["einstellungen"]["schliesztage"] = schliesztage_str

    # --- Gerichte ---
    with st.expander("Gerichte pro Wochentag", expanded=False):
        gerichte = config.get("gerichte", {})
        for i, tag in enumerate(WOCHENTAGE):
            gerichte[str(i)] = st.text_input(
                tag, value=gerichte.get(str(i), ""), key=f"gericht_{i}"
            )
        config["gerichte"] = gerichte

    # --- Eltern ---
    with st.expander("Eltern verwalten", expanded=False):
        eltern = config.get("eltern", [])

        with st.form("neues_elternteil", clear_on_submit=True):
            st.subheader("Elternteil hinzufügen")
            neuer_name = st.text_input("Name")
            neues_telefon = st.text_input("Telefon")
            neuer_vorstand = st.checkbox("Vorstandsmitglied")
            neuer_wochentage = st.multiselect(
                "Erlaubte Wochentage (leer = alle)",
                options=list(range(5)),
                format_func=lambda x: WOCHENTAGE[x],
            )
            if st.form_submit_button("Hinzufügen"):
                if neuer_name and not any(e["name"] == neuer_name for e in eltern):
                    eltern.append({
                        "name": neuer_name,
                        "telefon": neues_telefon,
                        "ist_vorstand": neuer_vorstand,
                        "erlaubte_wochentage": neuer_wochentage,
                        "sperrzeiten": [],
                    })
                    config["eltern"] = eltern
                    st.success(f"{neuer_name} hinzugefügt.")

        if eltern:
            st.divider()
            for idx, elternteil in enumerate(eltern):
                with st.expander(elternteil["name"], expanded=False):
                    elternteil["telefon"] = st.text_input(
                        "Telefon", value=elternteil.get("telefon", ""), key=f"tel_{idx}"
                    )
                    elternteil["ist_vorstand"] = st.checkbox(
                        "Vorstandsmitglied", value=elternteil.get("ist_vorstand", False), key=f"vorstand_{idx}"
                    )
                    elternteil["erlaubte_wochentage"] = st.multiselect(
                        "Erlaubte Wochentage (leer = alle)",
                        options=list(range(5)),
                        default=elternteil.get("erlaubte_wochentage", []),
                        format_func=lambda x: WOCHENTAGE[x],
                        key=f"wochentage_{idx}",
                    )
                    # Sperrzeiten
                    sperrzeiten = elternteil.get("sperrzeiten", [])
                    neue_sperre = st.date_input("Sperrzeit hinzufügen", key=f"sperre_{idx}")
                    sperre_col1, sperre_col2 = st.columns(2)
                    with sperre_col1:
                        if st.button("Sperrzeit eintragen", key=f"btn_sperre_{idx}"):
                            if neue_sperre.isoformat() not in sperrzeiten:
                                sperrzeiten.append(neue_sperre.isoformat())
                                elternteil["sperrzeiten"] = sperrzeiten
                    if sperrzeiten:
                        st.write("Sperrzeiten:")
                        for sp in sorted(sperrzeiten):
                            sc1, sc2 = st.columns([3, 1])
                            sc1.write(sp)
                            if sc2.button("✕", key=f"del_sp_{idx}_{sp}"):
                                sperrzeiten.remove(sp)
                                elternteil["sperrzeiten"] = sperrzeiten

                    if st.button("Elternteil entfernen", key=f"del_elternteil_{idx}"):
                        eltern.pop(idx)
                        config["eltern"] = eltern
                        st.rerun()

        config["eltern"] = eltern

    # --- Kinder ---
    with st.expander("Kinder verwalten", expanded=False):
        kinder = config.get("kinder", [])
        eltern_namen = [e["name"] for e in config.get("eltern", [])]

        with st.form("neues_kind", clear_on_submit=True):
            neues_kind_name = st.text_input("Name des Kindes")
            kind_eltern = st.multiselect("Zugehörige Eltern", options=eltern_namen)
            if st.form_submit_button("Kind hinzufügen"):
                if neues_kind_name:
                    kinder.append({"name": neues_kind_name, "eltern": kind_eltern})
                    config["kinder"] = kinder

        for idx, kind in enumerate(kinder):
            col1, col2 = st.columns([3, 1])
            col1.write(f"**{kind['name']}** – {', '.join(kind.get('eltern', []))}")
            if col2.button("✕", key=f"del_kind_{idx}"):
                kinder.pop(idx)
                config["kinder"] = kinder
                st.rerun()

        config["kinder"] = kinder

    st.divider()
    if st.button("Konfiguration speichern", type="primary"):
        speichere_config(config)
        st.success("Gespeichert.")


# === HAUPTBEREICH ===

tab_plan, tab_historie, tab_statistik = st.tabs(["Plan", "Historie", "Statistik"])

with tab_plan:
    col_gen, col_pdf = st.columns([2, 1])

    with col_gen:
        if st.button("Plan generieren", type="primary"):
            startdatum = str_zu_datum(config["einstellungen"]["startdatum"])
            monate = config["einstellungen"]["planungsmonate"]
            enddatum = startdatum + relativedelta(months=monate) - timedelta(days=1)
            st.session_state.plan = generiere_plan(
                config, st.session_state.historie, startdatum, enddatum
            )
            st.success(f"Plan für {monate} Monate ab {startdatum.strftime('%d.%m.%Y')} generiert.")

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
            st.download_button(
                "PDF herunterladen",
                data=pdf_bytes,
                file_name="kochplan.pdf",
                mime="application/pdf",
            )

        if st.button("Plan als Historie speichern"):
            neue_einsaetze = berechne_einsaetze(plan)
            for name, anzahl in neue_einsaetze.items():
                st.session_state.historie[name] = st.session_state.historie.get(name, 0) + anzahl
            speichere_historie(st.session_state.historie)
            st.success("Einsätze zur Historie hinzugefügt.")

        # Plan anzeigen: wochenweise HTML-Tabelle
        eltern_namen = [""] + [e["name"] for e in config["eltern"]]
        kind_mapping = elternteil_zu_kinder(config)
        feiertage_set = {d for d in config["einstellungen"].get("feiertage", [])}
        gerichte = config.get("gerichte", {})

        plan_index = {e["datum"]: e for e in plan}
        if plan:
            erster = date.fromisoformat(plan[0]["datum"])
            letzter = date.fromisoformat(plan[-1]["datum"])
            montag_start = erster - timedelta(days=erster.weekday())
            freitag_ende = letzter + timedelta(days=(4 - letzter.weekday()))

            wochen: list[list[date]] = []
            d = montag_start
            while d <= freitag_ende:
                wochen.append([d + timedelta(days=i) for i in range(5)])
                d += timedelta(days=7)

            WOCHENTAGE_LANG = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]

            kopf_zellen = ""
            for i, tag in enumerate(WOCHENTAGE_LANG):
                gericht = gerichte.get(str(i), "")
                kopf_zellen += f'<th>{tag}<br><span class="gericht">{gericht}</span></th>'

            zeilen_html = ""
            for w_idx, woche in enumerate(wochen):
                kw = woche[0].isocalendar()[1]
                zellen = ""
                for tag in woche:
                    datum_str = tag.isoformat()
                    eintrag = plan_index.get(datum_str)

                    if datum_str in feiertage_set:
                        zellen += (
                            f'<td><span class="datum">{tag.strftime("%d.%m.%Y")}</span>'
                            f'<span class="sonder">Feiertag</span></td>'
                        )
                    elif eintrag is None:
                        zellen += '<td class="leer"></td>'
                    elif eintrag.get("ist_schliesztag"):
                        zellen += (
                            f'<td><span class="datum">{tag.strftime("%d.%m.%Y")}</span>'
                            f'<span class="sonder">Schließtag</span></td>'
                        )
                    else:
                        elternteil = eintrag.get("elternteil", "")
                        kinder = kind_mapping.get(elternteil, [])
                        anzeige = ", ".join(kinder) if kinder else elternteil if elternteil else "–"
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

            html = f"""
<style>
  .kochplan {{ width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 14px; }}
  .kochplan th {{
    background-color: #4A7C59; color: white; padding: 8px 10px;
    text-align: center; border: 1px solid #3a6347;
  }}
  .kochplan th .gericht {{ font-size: 0.78em; font-weight: normal; color: #CCEEDD; display: block; margin-top: 2px; }}
  .kochplan td {{ padding: 6px 10px; vertical-align: top; border: 1px solid #CCCCCC; min-width: 110px; }}
  .kochplan td.kw-zelle {{
    background-color: #E8F0EA !important; font-weight: bold;
    text-align: center; vertical-align: middle; white-space: nowrap;
  }}
  .kochplan td.leer {{ background-color: #F8F8F8; }}
  .kochplan .datum {{ font-size: 0.75em; color: #999999; display: block; margin-bottom: 2px; }}
  .kochplan .name {{ font-weight: bold; display: block; }}
  .kochplan .sonder {{ font-style: italic; color: #AAAAAA; display: block; }}
  .kochplan .manuell {{ color: #E07020; font-style: normal; font-size: 0.85em; }}
</style>
<table class="kochplan">
  <thead>
    <tr><th>Woche</th>{kopf_zellen}</tr>
  </thead>
  <tbody>
    {zeilen_html}
  </tbody>
</table>
"""
            st.markdown(html, unsafe_allow_html=True)

        # Manuelle Bearbeitung
        st.divider()
        with st.expander("Plan manuell bearbeiten", expanded=False):
            for idx, eintrag in enumerate(plan):
                if eintrag.get("ist_schliesztag"):
                    continue
                d = date.fromisoformat(eintrag["datum"])
                cols = st.columns([2, 2, 3, 3, 1])
                cols[0].write(d.strftime("%d.%m.%Y"))
                cols[1].write(eintrag["wochentag_name"])
                cols[2].write(eintrag["gericht"])
                aktueller_elternteil = eintrag.get("elternteil", "")
                neuer_elternteil = cols[3].selectbox(
                    "Elternteil",
                    options=eltern_namen,
                    index=eltern_namen.index(aktueller_elternteil) if aktueller_elternteil in eltern_namen else 0,
                    format_func=lambda name: ", ".join(kind_mapping.get(name, [])) if name and kind_mapping.get(name) else name,
                    key=f"select_{idx}",
                    label_visibility="collapsed",
                )
                if neuer_elternteil != aktueller_elternteil:
                    plan[idx]["elternteil"] = neuer_elternteil
                    plan[idx]["manuell_geaendert"] = True
                if eintrag.get("manuell_geaendert"):
                    cols[4].markdown("✏️")


with tab_historie:
    st.header("Historische Einsätze")
    historie = st.session_state.historie
    if not historie:
        st.info("Noch keine historischen Einsätze gespeichert.")
    else:
        for name, anzahl in sorted(historie.items(), key=lambda x: -x[1]):
            st.write(f"**{name}**: {anzahl} Einsatz/Einsätze")

    st.divider()
    if st.button("Historie zurücksetzen", type="secondary"):
        st.session_state.historie = {}
        speichere_historie({})
        st.success("Historie zurückgesetzt.")


with tab_statistik:
    st.header("Statistik")
    plan = st.session_state.plan
    if not plan:
        st.info("Erst einen Plan generieren.")
    else:
        einsaetze = berechne_einsaetze(plan)
        historische = st.session_state.historie

        st.subheader("Einsätze im aktuellen Plan")
        for elternteil in config["eltern"]:
            name = elternteil["name"]
            aktuell = einsaetze.get(name, 0)
            gesamt = historische.get(name, 0) + aktuell
            vorstand = " (Vorstand)" if elternteil.get("ist_vorstand") else ""
            st.metric(
                label=f"{name}{vorstand}",
                value=f"{aktuell} aktuell",
                delta=f"{gesamt} gesamt",
            )
