import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import datetime
import os

st.set_page_config(page_title="Kosztorys Elektryczny", layout="centered")
# --- SYSTEM LOGOWANIA ---
MOJE_HASLO = "Elektro2026"  # <-- Tutaj wpisz swoje własne, tajne hasło

# Sprawdzenie, czy użytkownik jest już zalogowany w obecnej sesji
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔒 Dostęp zablokowany")
    st.info("Aplikacja chroniona hasłem dostępowym wykonawcy.")
    
    password_input = st.text_input("Wprowadź hasło dostępu:", type="password")
    
    if st.button("Zaloguj się", use_container_width=True):
        if password_input == MOJE_HASLO:
            st.session_state.logged_in = True
            st.rerun()  # Przeładuj stronę, aby pokazać kosztorys
        else:
            st.error("Nieprawidłowe hasło. Odmowa dostępu.")
            
    # Zatrzymujemy wykonywanie dalszej części kodu (kosztorysu), dopóki brak autoryzacji
    st.stop()

# (Opcjonalnie) Przycisk wylogowania w menu bocznym:
if st.sidebar.button("Wyloguj się"):
    st.session_state.logged_in = False
    st.rerun()

st.title("⚡ Kosztorys Robót Elektrycznych")
st.caption("Aplikacja do kalkulacji i generowania ofert PDF")

# Czcionki z polskimi znakami
font_registered = False
windows_arial = "C:/Windows/Fonts/arial.ttf"
windows_arial_bd = "C:/Windows/Fonts/arialbd.ttf"

if os.path.exists(windows_arial) and os.path.exists(windows_arial_bd):
    pdfmetrics.registerFont(TTFont("CustomFont", windows_arial))
    pdfmetrics.registerFont(TTFont("CustomFont-Bold", windows_arial_bd))
    FONT_NORMAL = "CustomFont"
    FONT_BOLD = "CustomFont-Bold"
    font_registered = True
else:
    FONT_NORMAL = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"

with st.expander("1. Dane zlecenia", expanded=True):
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        firma = st.text_input("Twoja firma (Wykonawca):", value="Elektro-Instal Jan Kowalski, NIP: 123-456-78-90")
        klient = st.text_input("Klient / Inwestor:", value="Jan Nowak")
    with col_k2:
        nr_oferty = st.text_input("Numer oferty:", value="OF/2026/01")
        adres = st.text_input("Adres inwestycji:", value="ul. Leśna 5, Warszawa")

with st.expander("2. Instalacja Wewnętrzna", expanded=False):
    st.markdown("**Punkty wewnętrzne**")
    c1, c2 = st.columns(2)
    in_pt_pwr = c1.number_input("Gniazda, łączniki, lampy (szt.):", value=40, step=1)
    in_pt_pwr_r = c2.number_input("Stawka za punkt 230V (zł):", value=85.0, step=5.0)

    in_pt_lan = c1.number_input("Punkty TV i LAN (szt.):", value=8, step=1)
    in_pt_lan_r = c2.number_input("Stawka TV/LAN (zł):", value=90.0, step=5.0)

    in_pt_alm = c1.number_input("Punkty alarmu wewn. (szt.):", value=6, step=1)
    in_pt_alm_r = c2.number_input("Stawka za alarm wewn. (zł):", value=80.0, step=5.0)

    st.markdown("**Przewody wewnętrzne (metry / stawka)**")
    c3, c4 = st.columns(2)
    m_ydyp315 = c3.number_input("YDYp 3x1.5 (lampy) [mb]:", value=120, step=10)
    r_ydyp315 = c4.number_input("Stawka YDYp 3x1.5 (zł/m):", value=8.0, step=1.0)

    m_ydyp415 = c3.number_input("YDYp 4x1.5 (schodowe/lampy) [mb]:", value=60, step=10)
    r_ydyp415 = c4.number_input("Stawka YDYp 4x1.5 (zł/m):", value=8.0, step=1.0)

    m_ydyp325 = c3.number_input("YDYp 3x2.5 (gniazda) [mb]:", value=220, step=10)
    r_ydyp325 = c4.number_input("Stawka YDYp 3x2.5 (zł/m):", value=8.0, step=1.0)

    m_ydyp525 = c3.number_input("YDYp 5x2.5 (indukcja) [mb]:", value=25, step=5)
    r_ydyp525 = c4.number_input("Stawka YDYp 5x2.5 (zł/m):", value=10.0, step=1.0)

    m_ytdy_in = c3.number_input("YTDY 6x0.5 (alarm) [mb]:", value=80, step=10)
    r_ytdy_in = c4.number_input("Stawka YTDY wewn. (zł/m):", value=6.0, step=1.0)

    m_utp_in = c3.number_input("Skrętka UTP kat. 6 [mb]:", value=100, step=10)
    r_utp_in = c4.number_input("Stawka Skrętka (zł/m):", value=7.0, step=1.0)

    m_opt = c3.number_input("Kabel światłowodowy [mb]:", value=20, step=5)
    r_opt = c4.number_input("Stawka światłowód (zł/m):", value=10.0, step=1.0)

    m_tv_in = c3.number_input("Kabel antenowy TV [mb]:", value=50, step=10)
    r_tv_in = c4.number_input("Stawka antenowy (zł/m):", value=7.0, step=1.0)

with st.expander("3. Instalacja Zewnętrzna", expanded=False):
    st.markdown("**Punkty i montaż zewnętrzny**")
    c5, c6 = st.columns(2)
    out_pt_pwr = c5.number_input("Gniazda i łączniki zewn. (szt.):", value=4, step=1)
    out_pt_pwr_r = c6.number_input("Stawka gniazdo zewn. (zł):", value=95.0, step=5.0)

    out_pt_lamp = c5.number_input("Lampy zewn. elewacja/podbitka (szt.):", value=8, step=1)
    out_pt_lamp_r = c6.number_input("Stawka lampa zewn. (zł):", value=90.0, step=5.0)

    out_pt_ant = c5.number_input("Montaż anteny TV (kpl.):", value=1, step=1)
    out_pt_ant_r = c6.number_input("Stawka antena (zł):", value=200.0, step=10.0)

    out_pt_cam = c5.number_input("Kamery CCTV montaż (szt.):", value=4, step=1)
    out_pt_cam_r = c6.number_input("Stawka kamera CCTV (zł):", value=180.0, step=10.0)

    out_pt_alm = c5.number_input("Czujki alarmu zewn. (szt.):", value=2, step=1)
    out_pt_alm_r = c6.number_input("Stawka czujka zewn. (zł):", value=110.0, step=10.0)

    st.markdown("**Przewody zewnętrzne (metry / stawka)**")
    c7, c8 = st.columns(2)
    m_ykyo315 = c7.number_input("YKYo 3x1.5 (lampy ziemia) [mb]:", value=45, step=5)
    r_ykyo315 = c8.number_input("Stawka YKYo 3x1.5 (zł/m):", value=12.0, step=1.0)

    m_ykyo325 = c7.number_input("YKYo 3x2.5 (gniazda ziemia) [mb]:", value=30, step=5)
    r_ykyo325 = c8.number_input("Stawka YKYo 3x2.5 (zł/m):", value=12.0, step=1.0)

    m_ytdy_out = c7.number_input("YTDY 6x0.5 zewn. [mb]:", value=35, step=5)
    r_ytdy_out = c8.number_input("Stawka YTDY zewn. (zł/m):", value=9.0, step=1.0)

    m_utp_out = c7.number_input("Skrętka monitoringu zewn. [mb]:", value=80, step=10)
    r_utp_out = c8.number_input("Stawka monitoring zewn. (zł/m):", value=10.0, step=1.0)

    m_tv_out = c7.number_input("Kabel antenowy zewn. [mb]:", value=25, step=5)
    r_tv_out = c8.number_input("Stawka antena zewn. (zł/m):", value=10.0, step=1.0)

    m_dom = c7.number_input("Kabel domofonu [mb]:", value=30, step=5)
    r_dom = c8.number_input("Stawka domofon (zł/m):", value=12.0, step=1.0)

    m_gate = c7.number_input("Kabel do bramy [mb]:", value=35, step=5)
    r_gate = c8.number_input("Stawka brama (zł/m):", value=12.0, step=1.0)

with st.expander("4. Rozdzielnica i Pomiary", expanded=False):
    c9, c10 = st.columns(2)
    box_mount = c9.number_input("Montaż obudowy rozdzielnicy (ryczałt zł):", value=300.0, step=50.0)
    circuits_qty = c9.number_input("Liczba podłączanych obwodów:", value=16, step=1)
    circuits_rate = c10.number_input("Stawka za obwód (zł):", value=65.0, step=5.0)

    box_pwr_qty = c9.number_input("Gniazdo siłowe 5x32A (szt.):", value=1, step=1)
    box_pwr_rate = c10.number_input("Montaż gniazda siłowego (zł):", value=160.0, step=10.0)

    test_rate = c10.number_input("Pomiar za 1 obwód (zł):", value=25.0, step=5.0)
    ground_flat = c9.number_input("Badanie uziemienia (ryczałt zł):", value=150.0, step=20.0)

with st.expander("5. Przyłącze / WLZ", expanded=False):
    c11, c12 = st.columns(2)
    wlz_cable_m = c11.number_input("Kabel zasilający WLZ [mb]:", value=25, step=5)
    wlz_cable_r = c12.number_input("Układanie WLZ (zł/m):", value=22.0, step=2.0)

    wlz_dig_m = c11.number_input("Wykop pod WLZ [mb]:", value=25, step=5)
    wlz_dig_r = c12.number_input("Stawka za wykop (zł/m):", value=45.0, step=5.0)

    wlz_conn = c11.number_input("Przebicie fundamentu + ZK (ryczałt zł):", value=400.0, step=50.0)

vat_dict = {"8% (Mieszkaniowy)": 0.08, "23% (Komercyjny / Firma)": 0.23, "0% (Zwolnienie z VAT)": 0.00}
vat_choice = st.selectbox("Wybierz stawkę podatku VAT:", list(vat_dict.keys()))
vat_rate = vat_dict[vat_choice]

items = [
    ("Montaż punktów 230V (gniazda, włączniki, lampy)", in_pt_pwr, "szt.", in_pt_pwr_r),
    ("Montaż punktów teletechnicznych (TV, LAN RJ45)", in_pt_lan, "szt.", in_pt_lan_r),
    ("Montaż punktów alarmowych (czujki, manipulator)", in_pt_alm, "szt.", in_pt_alm_r),
    ("Układanie przewodu oświetleniowego YDYp 3x1.5", m_ydyp315, "mb", r_ydyp315),
    ("Układanie przewodu oświetleniowego YDYp 4x1.5", m_ydyp415, "mb", r_ydyp415),
    ("Układanie przewodu gniazdowego YDYp 3x2.5", m_ydyp325, "mb", r_ydyp325),
    ("Układanie przewodu zasilania płyty YDYp 5x2.5", m_ydyp525, "mb", r_ydyp525),
    ("Układanie przewodu alarmowego YTDY 6x0.5", m_ytdy_in, "mb", r_ytdy_in),
    ("Układanie skrętki komputerowej U/UTP kat. 6", m_utp_in, "mb", r_utp_in),
    ("Układanie kabla światłowodowego", m_opt, "mb", r_opt),
    ("Układanie kabla antenowego TV", m_tv_in, "mb", r_tv_in),
    ("Montaż gniazd i włączników zewn. hermetycznych", out_pt_pwr, "szt.", out_pt_pwr_r),
    ("Montaż lamp zewn. (elewacja, podbitka)", out_pt_lamp, "szt.", out_pt_lamp_r),
    ("Montaż anteny telewizyjnej z uziemieniem", out_pt_ant, "kpl.", out_pt_ant_r),
    ("Montaż i zarobienie kamer monitoringu CCTV", out_pt_cam, "szt.", out_pt_cam_r),
    ("Montaż czujników alarmu zewnętrznych", out_pt_alm, "szt.", out_pt_alm_r),
    ("Układanie kabla ziemnego oświetlenia YKYo 3x1.5", m_ykyo315, "mb", r_ykyo315),
    ("Układanie kabla ziemnego gniazd YKYo 3x2.5", m_ykyo325, "mb", r_ykyo325),
    ("Układanie kabla alarmu zewnętrznego YTDY 6x0.5", m_ytdy_out, "mb", r_ytdy_out),
    ("Układanie skrętki monitoringu zewn. U/UTP kat. 6", m_utp_out, "mb", r_utp_out),
    ("Układanie kabla antenowego zewnętrznego", m_tv_out, "mb", r_tv_out),
    ("Układanie kabla do domofonu / wideodomofonu", m_dom, "mb", r_dom),
    ("Układanie kabla sterowania i zasilania bramy", m_gate, "mb", r_gate),
    ("Montaż i osadzenie obudowy rozdzielnicy", 1 if box_mount > 0 else 0, "kpl.", box_mount),
    ("Wprowadzenie i podłączenie obwodów rozdzielnicy", circuits_qty, "obw.", circuits_rate),
    ("Montaż i podłączenie gniazda siłowego 5x32A", box_pwr_qty, "szt.", box_pwr_rate),
    ("Pomiary odbiorcze instalacji (ochrona p-porażeniowa)", circuits_qty, "obw.", test_rate),
    ("Badanie uziemienia i protokół odbiorczy", 1 if ground_flat > 0 else 0, "kpl.", ground_flat),
    ("Układanie kabla zasilającego WLZ w wykopie", wlz_cable_m, "mb", wlz_cable_r),
    ("Wykop pod kabel zasilający WLZ", wlz_dig_m, "mb", wlz_dig_r),
    ("Przejście fundamentowe + podłączenie w ZK", 1 if wlz_conn > 0 else 0, "kpl.", wlz_conn)
]

total_net = sum(q * r for _, q, _, r in items if q > 0 and r > 0)
total_vat = total_net * vat_rate
total_gross = total_net + total_vat

st.divider()
k1, k2, k3 = st.columns(3)
k1.metric("Suma Netto", f"{total_net:,.2f} zł")
k2.metric("Podatek VAT", f"{total_vat:,.2f} zł")
k3.metric("DO ZAPŁATY (Brutto)", f"{total_gross:,.2f} zł")

def create_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=35, rightMargin=35, topMargin=35, bottomMargin=35)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=16, leading=20, textColor=colors.HexColor("#1e40af"))
    text_bold = ParagraphStyle('TBold', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=9, leading=12)
    text_normal = ParagraphStyle('TNorm', parent=styles['Normal'], fontName=FONT_NORMAL, fontSize=8, leading=10)
    text_center = ParagraphStyle('TCtr', parent=text_normal, alignment=1)
    text_right = ParagraphStyle('TRgt', parent=text_normal, alignment=2)
    header_style = ParagraphStyle('Hdr', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=8, leading=10, textColor=colors.HexColor("#0f172a"))

    elements = []
    
    elements.append(Paragraph("KOSZTORYS ROBÓT ELEKTRYCZNYCH", title_style))
    elements.append(Paragraph(f"Nr oferty: <b>{nr_oferty}</b> | Data: {datetime.date.today().strftime('%d.%m.%Y')}", text_normal))
    elements.append(Spacer(1, 12))

    parties_data = [
        [Paragraph(f"<b>WYKONAWCA:</b><br/>{firma}", text_normal),
         Paragraph(f"<b>INWESTOR:</b><br/>{klient}<br/>Adres: {adres}", text_normal)]
    ]
    t_parties = Table(parties_data, colWidths=[260, 260])
    t_parties.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(t_parties)
    elements.append(Spacer(1, 14))

    table_data = [[
        Paragraph("Zakres robót montażowych", header_style),
        Paragraph("Ilość", header_style),
        Paragraph("Jm", header_style),
        Paragraph("Cena j.", header_style),
        Paragraph("Wartość", header_style)
    ]]

    for name, qty, unit, rate in items:
        if qty > 0 and rate > 0:
            val = qty * rate
            table_data.append([
                Paragraph(name, text_normal),
                Paragraph(str(qty), text_center),
                Paragraph(unit, text_center),
                Paragraph(f"{rate:.2f} zł", text_right),
                Paragraph(f"{val:.2f} zł", text_right)
            ])

    t_items = Table(table_data, colWidths=[270, 50, 40, 75, 85])
    t_items.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_items)
    elements.append(Spacer(1, 12))

    summary_data = [
        [Paragraph("Suma Netto:", text_normal), Paragraph(f"{total_net:,.2f} zł", text_right)],
        [Paragraph(f"Podatek VAT ({int(vat_rate*100)}%):", text_normal), Paragraph(f"{total_vat:,.2f} zł", text_right)],
        [Paragraph("<b>DO ZAPŁATY (Brutto):</b>", text_bold), Paragraph(f"<b>{total_gross:,.2f} zł</b>", text_right)]
    ]
    t_sum = Table(summary_data, colWidths=[120, 100], hAlign='RIGHT')
    t_sum.setStyle(TableStyle([
        ('LINEABOVE', (0,2), (1,2), 1, colors.black),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elements.append(t_sum)

    elements.append(Spacer(1, 25))
    elements.append(Paragraph("Podpis wykonawcy: ...........................................", text_normal))

    doc.build(elements)
    buffer.seek(0)
    return buffer

pdf_data = create_pdf()
st.download_button(
    label="📥 Pobierz gotowy Kosztorys w PDF",
    data=pdf_data,
    file_name=f"Kosztorys_{nr_oferty.replace('/', '_')}.pdf",
    mime="application/pdf",
    use_container_width=True
)
