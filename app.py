import os
import streamlit as st
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from daten import lade_config, speichere_config, lade_historie, speichere_historie, str_zu_datum, DATEN_VERZEICHNIS
from planer import generiere_plan, berechne_einsaetze, validiere_plan, WOCHENTAGE
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

    # --- Planungszeitraum ---
    with st.expander("Planungszeitraum", expanded=False):
        planungsmonate = st.number_input(
            "Monate", min_value=1, max_value=12,
            value=config["einstellungen"].get("planungsmonate", 3),
            key="planungsmonate",
        )
        startdatum = st.date_input(
            "Startdatum",
            value=str_zu_datum(config["einstellungen"].get("startdatum", date.today().isoformat())),
            key="startdatum",
        )
        config["einstellungen"]["planungsmonate"] = planungsmonate
        config["einstellungen"]["startdatum"] = startdatum.isoformat()

    # --- Feiertage ---
    with st.expander("Feiertage (werden übersprungen)", expanded=False):
        feiertage_str = config["einstellungen"].get("feiertage", [])
        neuer_feiertag = st.date_input("Datum hinzufügen", key="neuer_feiertag")
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
            for sz in sorted(schliesztage_str):
                c1, c2 = st.columns([3, 1])
                c1.write(sz)
                if c2.button("✕", key=f"del_sz_{sz}"):
                    schliesztage_str.remove(sz)
                    config["einstellungen"]["schliesztage"] = schliesztage_str

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
            neues_telefon = st.text_input("Telefon")
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
                        "telefon": neues_telefon,
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
                    kind["telefon"] = st.text_input(
                        "Telefon", value=kind.get("telefon", ""), key=f"tel_{idx}"
                    )
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
                    neue_sperre = st.date_input("Sperrzeit hinzufügen", key=f"sperre_{idx}")
                    if st.button("Sperrzeit eintragen", key=f"btn_sperre_{idx}"):
                        if neue_sperre.isoformat() not in sperrzeiten:
                            sperrzeiten.append(neue_sperre.isoformat())
                            kind["sperrzeiten"] = sperrzeiten
                    if sperrzeiten:
                        st.write("Sperrzeiten:")
                        for sp in sorted(sperrzeiten):
                            sc1, sc2 = st.columns([3, 1])
                            sc1.write(sp)
                            if sc2.button("✕", key=f"del_sp_{idx}_{sp}"):
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

tab_plan, tab_historie, tab_statistik = st.tabs(["Plan", "Historie", "Statistik"])

with tab_plan:
    col_gen, col_pdf = st.columns([2, 1])

    with col_gen:
        if st.button("Plan generieren", type="primary"):
            start = str_zu_datum(config["einstellungen"]["startdatum"])
            monate = config["einstellungen"]["planungsmonate"]
            ende = start + relativedelta(months=monate) - timedelta(days=1)
            st.session_state.plan = generiere_plan(config, st.session_state.historie, start, ende)
            st.success(f"Plan für {monate} Monate ab {start.strftime('%d.%m.%Y')} generiert.")

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
            for name, anzahl in berechne_einsaetze(plan).items():
                st.session_state.historie[name] = st.session_state.historie.get(name, 0) + anzahl
            speichere_historie(st.session_state.historie)
            st.success("Einsätze zur Historie hinzugefügt.")

        # Plan anzeigen: wochenweise HTML-Tabelle
        feiertage_set = {d for d in config["einstellungen"].get("feiertage", [])}
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
</table>
"""
        st.markdown(html, unsafe_allow_html=True)

        # Manuelle Bearbeitung
        st.divider()
        kinder_namen = [""] + [k["name"] for k in config["kinder"]]
        with st.expander("Plan manuell bearbeiten", expanded=False):
            for idx, eintrag in enumerate(plan):
                if eintrag.get("ist_schliesztag"):
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
        for kind in config["kinder"]:
            name = kind["name"]
            aktuell = einsaetze.get(name, 0)
            gesamt = historische.get(name, 0) + aktuell
            vorstand = " (Vorstand)" if kind.get("ist_vorstand") else ""
            st.metric(
                label=f"{name}{vorstand}",
                value=f"{aktuell} aktuell",
                delta=f"{gesamt} gesamt",
            )
