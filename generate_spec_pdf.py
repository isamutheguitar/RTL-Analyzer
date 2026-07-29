"""
generate_spec_pdf.py
Dual-Channel RTL Analyzer -- Software Specification & Measurement Logic PDF Generator
Requires: reportlab   (pip install reportlab)
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from datetime import datetime
import os

# -- Japanese CID font (built-in, no external file needed) --
JP_FONT = "HeiseiKakuGo-W5"
pdfmetrics.registerFont(UnicodeCIDFont(JP_FONT))

OUT_PATH = os.path.join(os.path.expanduser("~"), "Downloads",
                        "RTL_Analyzer_Specification.pdf")

W, H = A4
MARGIN = 20 * mm

C_NAVY    = colors.HexColor("#0d1117")
C_BLUE    = colors.HexColor("#58a6ff")
C_CYAN    = colors.HexColor("#7ec8e3")
C_ORANGE  = colors.HexColor("#e8a87c")
C_GRAY    = colors.HexColor("#8b949e")
C_LIGHT   = colors.HexColor("#e6edf3")
C_DIVIDER = colors.HexColor("#30363d")
C_CODEBG  = colors.HexColor("#161b22")


def S(name, **kw):
    return ParagraphStyle(name, **kw)


# -- English styles (Helvetica / Courier -- ASCII-safe) --
sH2   = S("H2",   fontName="Helvetica-Bold", fontSize=15, leading=20,
          textColor=C_CYAN,   spaceAfter=4, spaceBefore=14)
sH3   = S("H3",   fontName="Helvetica-Bold", fontSize=11, leading=15,
          textColor=C_ORANGE, spaceAfter=3, spaceBefore=8)
sBody = S("Body", fontName="Helvetica", fontSize=9.5, leading=14,
          textColor=C_LIGHT,  spaceAfter=4, alignment=TA_JUSTIFY)
sMono = S("Mono", fontName="Courier", fontSize=8.5, leading=12,
          textColor=C_CYAN,  backColor=C_CODEBG, spaceAfter=4,
          leftIndent=8, borderPad=4)

# -- Japanese styles (HeiseiKakuGo-W5) --
sH2jp   = S("H2jp",   fontName=JP_FONT, fontSize=14, leading=20,
            textColor=C_CYAN,   spaceAfter=4, spaceBefore=14)
sH3jp   = S("H3jp",   fontName=JP_FONT, fontSize=11, leading=15,
            textColor=C_ORANGE, spaceAfter=3, spaceBefore=8)
sBodyjp = S("Bodyjp", fontName=JP_FONT, fontSize=9.5, leading=15,
            textColor=C_LIGHT,  spaceAfter=4, alignment=TA_JUSTIFY)
sBulljp = S("Bulljp", fontName=JP_FONT, fontSize=9.5, leading=15,
            textColor=C_LIGHT,  spaceAfter=2, leftIndent=14)


def divider():
    return HRFlowable(width="100%", thickness=0.5, color=C_DIVIDER,
                      spaceAfter=4, spaceBefore=4)


def sp(n=6):
    return Spacer(1, n)


def h2(t, jp=False):    return Paragraph(t, sH2jp   if jp else sH2)
def h3(t, jp=False):    return Paragraph(t, sH3jp   if jp else sH3)
def body(t, jp=False):  return Paragraph(t, sBodyjp if jp else sBody)
def bull(t, jp=False):  return Paragraph(t, sBulljp if jp else sBody)

# NOTE: mono() must ONLY contain ASCII text to avoid tofu/box characters.
def mono(t):            return Paragraph(t.replace("\n", "<br/>"), sMono)


def sec(title, jp=False):
    return KeepTogether([sp(8), h2(title, jp=jp), divider(), sp(2)])


def make_table(data, col_widths=None, jp=False):
    font_h = JP_FONT if jp else "Helvetica-Bold"
    font_b = JP_FONT if jp else "Helvetica"
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0),  C_CODEBG),
        ("TEXTCOLOR",      (0, 0), (-1, 0),  C_CYAN),
        ("FONTNAME",       (0, 0), (-1, 0),  font_h),
        ("FONTNAME",       (0, 1), (-1, -1), font_b),
        ("FONTSIZE",       (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.HexColor("#0d1117"), C_CODEBG]),
        ("TEXTCOLOR",      (0, 1), (-1, -1), C_LIGHT),
        ("GRID",           (0, 0), (-1, -1), 0.3, C_DIVIDER),
        ("TOPPADDING",     (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 4),
        ("LEFTPADDING",    (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 6),
    ]))
    return t


# ---------------------------------------------------------------------------
# Cover page
# ---------------------------------------------------------------------------
def cover():
    e = [sp(30)]
    e.append(Paragraph(
        '<font color="#58a6ff" size="28"><b>Dual-Channel RTL Analyzer</b></font>',
        S("cov1", alignment=TA_CENTER, leading=36)))
    e.append(sp(6))
    e.append(Paragraph(
        '<font color="#7ec8e3" size="13">'
        'Software Specification &amp; Measurement Logic</font>',
        S("cov2", alignment=TA_CENTER, leading=18)))
    e.append(sp(4))
    e.append(Paragraph(
        '<font color="#8b949e" size="10">'
        'Software Specification &amp; Measurement Logic</font>',
        S("cov3", fontName=JP_FONT, alignment=TA_CENTER, leading=14)))
    e.append(Paragraph(
        '<font color="#8b949e" size="10">'
        u'\u30bd\u30d5\u30c8\u30a6\u30a7\u30a2\u4ed5\u69d8\u66f8 &amp; '
        u'\u6e2c\u5b9a\u30ed\u30b8\u30c3\u30af\u89e3\u8aac</font>',
        S("cov4", fontName=JP_FONT, alignment=TA_CENTER, leading=14)))
    e.append(sp(20))
    e.append(HRFlowable(width="60%", thickness=1, color=C_BLUE,
                        hAlign="CENTER", spaceAfter=20))
    e.append(sp(10))
    meta = [
        ["Author",  "ISAMU the Guitar"],
        ["Website", "https://www.isamutheguitar.com"],
        ["Version", "1.0.0"],
        ["Date",    datetime.now().strftime("%Y-%m-%d")],
        ["Stack",   "Python 3.10+ | PySide6 | sounddevice | numpy / scipy / matplotlib"],
    ]
    e.append(make_table(meta, col_widths=[40 * mm, 120 * mm]))
    e.append(PageBreak())
    return e


# ---------------------------------------------------------------------------
# ENGLISH SECTION
# ---------------------------------------------------------------------------
def english():
    b = body
    e = []

    e.append(Paragraph(
        '<font color="#58a6ff" size="18"><b>-- English Section --</b></font>',
        S("se", alignment=TA_CENTER, leading=26)))
    e += [sp(4), divider(), sp(10)]

    # 1. Overview
    e.append(sec("1. Overview"))
    e.append(b("Dual-Channel RTL Analyzer is a native desktop application for measuring the "
               "pure processing latency (Round-Trip Latency) of audio equipment. A Gaussian "
               "impulse is sent simultaneously on L channel (direct loop-back = reference) and "
               "R channel (via DUT). The application detects both the L reference onset and the R DUT onset, "
               "then computes their time difference with sub-millisecond accuracy."))

    # 2. System Requirements
    e.append(sec("2. System Requirements"))
    e.append(make_table([
        ["Component",       "Requirement"],
        ["OS",              "Windows 10 / 11 (64-bit)"],
        ["Python",          "3.10 or later"],
        ["GUI",             "PySide6 (Qt 6)"],
        ["Audio I/O",       "sounddevice >= 0.4"],
        ["Numerics",        "numpy, scipy"],
        ["Plotting",        "matplotlib (QtAgg backend)"],
        ["Audio Driver",    "ASIO recommended; WDM/MME supported"],
        ["Audio Interface", "Stereo, >= 2 in / 2 out"],
    ], col_widths=[45 * mm, 115 * mm]))

    # 3. Architecture
    e.append(sec("3. Software Architecture"))
    e.append(make_table([
        ["Class",                     "Role"],
        ["MainWindow",                "Primary UI window (Qt main thread)"],
        ["MeasureWorker (QThread)",   "Blocking audio I/O + latency analysis"],
        ["LevelCheckWorker (QThread)","1 kHz level calibration"],
        ["WaveformCanvas",            "Matplotlib waveform display"],
        ["SetupDialog",               "Connection guide dialog"],
        ["ConnectionDiagramWidget",   "QPainter signal-flow diagram"],
    ], col_widths=[60 * mm, 100 * mm]))

    # 4. Connection Setup
    e.append(sec("4. Connection Setup"))
    e.append(make_table([
        ["Channel",     "Connection",                         "Purpose"],
        ["L ch (Ref)",  "L OUT -> L IN  (direct loop-back)",  "Timing reference"],
        ["R ch (DUT)",  "R OUT -> DUT In -> DUT Out -> R IN", "DUT latency path"],
    ], col_widths=[28 * mm, 82 * mm, 50 * mm]))
    e.append(b("Use the shortest possible cable for the L ch loop-back. "
               "The reported latency is the relative delay between the L impulse peak "
               "and the R DUT onset."))

    # 5. Measurement Sequence
    e.append(sec("5. Measurement Sequence"))
    e.append(make_table([
        ["Step", "Action",             "Detail"],
        ["1", "Signal generation",
         "Normalised Gaussian click (sigma=1, 1 ms) placed at sample offset 16 in a stereo buffer."],
        ["2", "Simultaneous play/rec",
         "sounddevice.playrec() -- single blocking call; both channels captured simultaneously."],
        ["3", "L ch onset detection",
         "l_onset = _find_onset(L_rec).  Detects the onset of the reference signal."],
        ["4", "R ch onset detection",
         "First sample after l_onset where |R_rec| exceeds the dynamic threshold (see Section 6.3)."],
        ["5", "Latency calculation",
         "delta_n = r_onset - l_onset  |  latency_ms = delta_n / sample_rate * 1000"],
        ["6", "Repeat",
         "Configured number of trials (1/3/10/30/100) with inter-trial interval."],
        ["7", "Statistics",
         "Mean, Max, Min, Std Dev. Trial closest to mean is displayed in the waveform plot."],
    ], col_widths=[8 * mm, 38 * mm, 114 * mm]))

    # 6. Measurement Algorithm
    e.append(sec("6. Measurement Algorithm -- Detail"))

    # 6.1 Reference signal
    e.append(h3("6.1  Reference Signal (L ch)"))
    e.append(b("A Gaussian-windowed impulse is used to balance temporal precision with "
               "spectral bandwidth. It has a smooth, well-defined peak that makes "
               "peak detection highly accurate:"))
    e.append(mono(
        "click_len = max(int(sample_rate * 0.001), 8)  # 1 ms or >= 8 samples\n"
        "t         = linspace(-3, 3, click_len)\n"
        "click     = exp(-t**2)                         # Gaussian envelope\n"
        "click    /= max(abs(click))                    # normalise to 0 dBFS\n"
        "# Placed at offset 16 on both L and R channels of the output buffer"))

    # 6.2 L ch onset
    e.append(h3("6.2  L Channel -- Onset Detection"))
    e.append(b("Using onset detection on both L and R channels eliminates systematic error. "
               "If L channel used peak detection while R channel used onset detection, "
               "the ~0.5 ms rise time of the 1 ms Gaussian impulse would introduce a systematic bias. "
               "Applying onset detection to both channels cancels out this rise-time delay perfectly:"))
    e.append(mono("l_onset = _find_onset(L_rec, noise_ref_end=noise_ref, search_start=0)"))
    e.append(b("This sample index serves as the temporal anchor (t = 0.0 ms) for computing "
               "the DUT delay and for setting the origin of the waveform plot time axis."))

    # 6.3 R ch onset
    e.append(h3("6.3  R Channel -- Onset Detection"))
    e.append(b("Unlike the reference impulse, the DUT signal may be modified by the device "
               "in several ways: it could be convolved with a long impulse response, "
               "have ringing added, or even have its polarity inverted. "
               "In all these cases, the absolute peak of the R channel signal may occur "
               "well after the true arrival of the signal at the DUT input. "
               "For this reason, onset detection -- finding the first moment the DUT begins "
               "to respond -- is more accurate than peak detection for R channel."))
    e.append(sp(4))
    e.append(b("<b>Step 1 -- Noise Floor Estimation</b>"))
    e.append(b("Before the signal arrives, the recording should contain only background noise. "
               "The first 10 ms of the recording (minimum 64 samples) is used to estimate the "
               "RMS noise floor. This gives us a reference level against which to judge "
               "whether a given sample is 'signal' or 'noise':"))
    e.append(mono(
        "noise_ref = max(64, int(sample_rate * 0.010))   # first 10 ms\n"
        "noise_rms = sqrt( mean( R_rec[:noise_ref] ** 2 ) )"))
    e.append(sp(4))
    e.append(b("<b>Step 2 -- Dynamic Threshold Calculation</b>"))
    e.append(b("A fixed threshold would fail across different signal levels and noise environments. "
               "Instead, two candidates are computed and the maximum is taken:"))
    e.append(bull("RMS candidate: 6 times the noise RMS. "
                  "This is sensitive enough to detect onset in quiet studio environments "
                  "without triggering on noise. The factor of 6 provides approximately "
                  "15 dB of headroom above the noise floor."))
    e.append(bull("Peak candidate: 1% of the maximum absolute value of the R channel "
                  "from l_peak onwards. This is a relative measure that adapts to signal "
                  "level and prevents false-negative detection in noisier environments "
                  "where the RMS candidate alone might be too high."))
    e.append(bull("Absolute minimum: 1e-5, preventing division errors in near-silence."))
    e.append(mono(
        "sig_peak  = max( abs( R_rec[l_onset:] ) )\n"
        "threshold = max(\n"
        "    noise_rms * 6.0,   # 6x RMS  -- sensitive in quiet environments\n"
        "    sig_peak  * 0.01,  # 1% peak -- fallback in noisy environments\n"
        "    1e-5               # absolute minimum\n"
        ")"))
    e.append(sp(4))
    e.append(b("<b>Step 3 -- First Threshold Crossing</b>"))
    e.append(b("The algorithm searches the absolute value of R_rec (from l_onset onwards) "
               "for the very first sample that exceeds the threshold. "
               "Using absolute value means the algorithm is polarity-independent: "
               "it correctly detects onset whether the DUT produces a positive peak, "
               "a negative dip, or any other response shape. "
               "If no sample exceeds the threshold (extremely rare failure mode), "
               "the peak position is used as a safe fallback:"))
    e.append(mono(
        "region  = abs( R_rec[l_onset:] )\n"
        "above   = where(region > threshold)\n"
        "\n"
        "if len(above) > 0:\n"
        "    r_onset = l_onset + above[0]        # first threshold crossing\n"
        "else:\n"
        "    r_onset = l_onset + argmax(region)  # fallback: peak position"))

    # 6.4 Latency
    e.append(h3("6.4  Latency Calculation"))
    e.append(b("Once both the L onset and R onset are known, the latency is straightforward:"))
    e.append(mono(
        "delta_n    = max(0, r_onset - l_onset)        # [samples]\n"
        "latency_ms = delta_n / sample_rate * 1000.0  # [ms]"))
    e.append(b("The max(0, ...) guard prevents negative values in the unlikely event "
               "that the onset is detected before the reference peak (e.g., due to "
               "pre-ringing or noise)."))

    # 7. Level Check
    e.append(sec("7. Level Check"))
    e.append(b("Plays a 1 kHz sine at -12 dBFS for 500 ms on both channels and measures "
               "peak levels of the recorded input:"))
    e.append(make_table([
        ["Level Range",    "Status",     "Colour", "Action"],
        ["<= -36 dBFS",   "Level Low",  "Orange", "Raise output level or input gain"],
        ["-36 to -1 dBFS","OK",         "Green",  "Ready to measure"],
        [">= -1 dBFS",    "Level High", "Red",    "Lower output level or input gain"],
    ], col_widths=[32 * mm, 24 * mm, 20 * mm, 84 * mm]))

    # 8. Configuration Reference
    e.append(sec("8. Configuration Reference"))
    e.append(make_table([
        ["Parameter",    "Options",                                       "Default"],
        ["Device Name",  "Free text",                                     "Target_Device"],
        ["Input Device", "System audio devices",                          "System default"],
        ["Output Device","System audio devices",                          "System default"],
        ["Sample Rate",  "44100 / 48000 / 88200 / 96000 / 192000 Hz",   "48000 Hz"],
        ["Trials",       "1 / 3 / 10 / 30 / 100",                       "10"],
        ["Interval",     "0.5 / 1.0 / 2.0 / 5.0 s",                    "1.0 s"],
        ["Trigger",      "Auto (1%) / 3% / 5% / 10% / 20% / 30% (Peak %)", "Auto (1%)"],
    ], col_widths=[38 * mm, 90 * mm, 32 * mm]))

    e.append(PageBreak())
    return e


# ---------------------------------------------------------------------------
# JAPANESE SECTION
# ---------------------------------------------------------------------------
def japanese():
    # All paragraph text in Japanese uses sBodyjp / sH2jp / sH3jp.
    # Code blocks (mono) must contain ASCII-only text to avoid tofu characters.
    def b(t):    return body(t, jp=True)
    def bl(t):   return bull(t, jp=True)
    def jh3(t):  return h3(t, jp=True)
    def jsec(t): return sec(t, jp=True)

    e = []
    e.append(Paragraph(
        u'<font color="#58a6ff" size="18"><b>\u2014 \u65e5\u672c\u8a9e\u30bb\u30af\u30b7\u30e7\u30f3 \u2014</b></font>',
        S("sjp", fontName=JP_FONT, alignment=TA_CENTER, leading=26)))
    e += [sp(4), divider(), sp(10)]

    # 1. 概要
    e.append(jsec(u"1. \u6982\u8981"))
    e.append(b(u"Dual-Channel RTL Analyzer \u306f\u3001\u30aa\u30fc\u30c7\u30a3\u30aa\u6a5f\u5668\u306e"
               u"\u7d14\u7c8b\u306a\u51e6\u7406\u30ec\u30a4\u30c6\u30f3\u30b7\u30fc\uff08Round-Trip Latency\uff09\u3092"
               u"\u81ea\u52d5\u8a08\u6e2c\u3059\u308b\u30cd\u30a4\u30c6\u30a3\u30d6\u30c7\u30b9\u30af\u30c8\u30c3\u30d7"
               u"\u30a2\u30d7\u30ea\u30b1\u30fc\u30b7\u30e7\u30f3\u3067\u3059\u3002"
               u"\u30ac\u30a6\u30b7\u30a2\u30f3\u30a4\u30f3\u30d1\u30eb\u30b9\u3092 L \u30c1\u30e3\u30f3\u30cd\u30eb"
               u"\uff08\u76f4\u7d50\u30eb\u30fc\u30d7\u30d0\u30c3\u30af\uff1d\u57fa\u6e96\uff09\u3068 R \u30c1\u30e3\u30f3\u30cd\u30eb"
               u"\uff08DUT \u7d4c\u7531\uff09\u306b\u540c\u6642\u9001\u4fe1\u3057\u3001L \u30c1\u30e3\u30f3\u30cd\u30eb\u306e"
               u"\u30d4\u30fc\u30af\u691c\u51fa\u3068 R \u30c1\u30e3\u30f3\u30cd\u30eb\u306e\u30aa\u30f3\u30bb\u30c3\u30c8\u691c\u51fa\u3092"
               u"\u7d44\u307f\u5408\u308f\u305b\u3066\u30b5\u30d6\u30df\u30ea\u79d2\u7cbe\u5ea6\u3067\u30ec\u30a4\u30c6\u30f3\u30b7\u30fc\u3092"
               u"\u7b97\u51fa\u3057\u307e\u3059\u3002"))

    # 2. システム要件
    e.append(jsec(u"2. \u30b7\u30b9\u30c6\u30e0\u8981\u4ef6"))
    e.append(make_table([
        [u"\u30b3\u30f3\u30dd\u30fc\u30cd\u30f3\u30c8", u"\u8981\u4ef6"],
        ["OS",              "Windows 10 / 11 (64-bit)"],
        ["Python",          u"3.10 \u4ee5\u4e0a"],
        [u"GUI \u30d5\u30ec\u30fc\u30e0\u30ef\u30fc\u30af", "PySide6 (Qt 6)"],
        [u"\u30aa\u30fc\u30c7\u30a3\u30aa I/O", "sounddevice >= 0.4"],
        [u"\u6570\u5024\u6f14\u7b97", "numpy, scipy"],
        [u"\u63cf\u753b", "matplotlib (QtAgg)"],
        [u"\u30aa\u30fc\u30c7\u30a3\u30aa\u30c9\u30e9\u30a4\u30d0\u30fc",
         u"ASIO \u63a8\u5968 / WDM\u30fbMME \u5bfe\u5fdc"],
        [u"\u30aa\u30fc\u30c7\u30a3\u30aa I/F",
         u"\u30b9\u30c6\u30ec\u30aa\u5bfe\u5fdc\uff08\u5165\u51fa\u529b\u5404 2ch \u4ee5\u4e0a\uff09"],
    ], col_widths=[52 * mm, 108 * mm], jp=True))

    # 3. アーキテクチャ
    e.append(jsec(u"3. \u30bd\u30d5\u30c8\u30a6\u30a7\u30a2\u30a2\u30fc\u30ad\u30c6\u30af\u30c1\u30e3"))
    e.append(make_table([
        [u"\u30af\u30e9\u30b9", u"\u5f79\u5272"],
        ["MainWindow", u"\u30e1\u30a4\u30f3 UI \u30a6\u30a3\u30f3\u30c9\u30a6\uff08Qt \u30e1\u30a4\u30f3\u30b9\u30ec\u30c3\u30c9\uff09"],
        ["MeasureWorker (QThread)", u"\u30d6\u30ed\u30c3\u30ad\u30f3\u30b0 \u30aa\u30fc\u30c7\u30a3\u30aa I/O \u30fb \u30ec\u30a4\u30c6\u30f3\u30b7\u30fc\u89e3\u6790"],
        ["LevelCheckWorker (QThread)", u"1 kHz \u30ec\u30d9\u30eb\u30ad\u30e3\u30ea\u30d6\u30ec\u30fc\u30b7\u30e7\u30f3"],
        ["WaveformCanvas", u"Matplotlib \u6ce2\u5f62\u8868\u793a"],
        ["SetupDialog", u"\u63a5\u7d9a\u65b9\u6cd5\u30ac\u30a4\u30c9\u30c0\u30a4\u30a2\u30ed\u30b0"],
        ["ConnectionDiagramWidget", u"QPainter \u4fe1\u53f7\u30d5\u30ed\u30fc\u56f3"],
    ], col_widths=[60 * mm, 100 * mm], jp=True))

    # 4. 接続構成
    e.append(jsec(u"4. \u63a5\u7d9a\u69cb\u6210"))
    e.append(make_table([
        [u"\u30c1\u30e3\u30f3\u30cd\u30eb", u"\u63a5\u7d9a\u65b9\u6cd5", u"\u76ee\u7684"],
        [u"L ch\uff08\u57fa\u6e96\uff09",
         u"L OUT -> L IN\uff08\u76f4\u7d50\u30eb\u30fc\u30d7\u30d0\u30c3\u30af\uff09",
         u"\u30bf\u30a4\u30df\u30f3\u30b0\u57fa\u6e96"],
        [u"R ch\uff08DUT\uff09",
         u"R OUT -> DUT \u5165\u529b -> DUT \u51fa\u529b -> R IN",
         u"DUT \u30ec\u30a4\u30c6\u30f3\u30b7\u30fc\u8a08\u6e2c"],
    ], col_widths=[28 * mm, 82 * mm, 50 * mm], jp=True))
    e.append(b(u"L \u30c1\u30e3\u30f3\u30cd\u30eb\u306e\u76f4\u7d50\u30b1\u30fc\u30d6\u30eb\u306f\u6975\u529b\u77ed\u3044\u3082\u306e\u3092\u4f7f\u7528\u3057\u3066\u304f\u3060\u3055\u3044\u3002"
               u"\u8868\u793a\u3055\u308c\u308b\u30ec\u30a4\u30c6\u30f3\u30b7\u30fc\u306f L \u30a4\u30f3\u30d1\u30eb\u30b9\u306e\u30d4\u30fc\u30af\u3068 R DUT \u30aa\u30f3\u30bb\u30c3\u30c8\u306e\u76f8\u5bfe\u7684\u306a\u6642\u9593\u5dee\u3067\u3059\u3002"))

    # 5. 測定シーケンス
    e.append(jsec(u"5. \u6e2c\u5b9a\u30b7\u30fc\u30b1\u30f3\u30b9"))
    e.append(make_table([
        [u"\u30b9\u30c6\u30c3\u30d7", u"\u64cd\u4f5c", u"\u8a73\u7d30"],
        ["1", u"\u4fe1\u53f7\u751f\u6210",
         u"\u6b63\u898f\u5316\u30ac\u30a6\u30b7\u30a2\u30f3\u30af\u30ea\u30c3\u30af\uff08\u03c3=1\u30011 ms\uff09\u3092\u30b5\u30f3\u30d7\u30eb\u30aa\u30d5\u30bb\u30c3\u30c8 16 \u306b\u914d\u7f6e\u3002"],
        ["2", u"\u540c\u6642\u518d\u751f\u30fb\u9332\u97f3",
         u"sounddevice.playrec() \u3067 1 \u56de\u306e\u30d6\u30ed\u30c3\u30ad\u30f3\u30b0\u30b3\u30fc\u30eb\u3002\u4e21 ch \u540c\u6642\u30ad\u30e3\u30d7\u30c1\u30e3\u3002"],
        ["3", u"L ch \u30aa\u30f3\u30bb\u30c3\u30c8\u691c\u51fa",
         u"l_onset = _find_onset(L_rec)\u3002\u57fa\u6e96\u4fe1\u53f7\u306e\u7acb\u3061\u4e0a\u304c\u308a\u3092\u691c\u51fa\u3002"],
        ["4", u"R ch \u30aa\u30f3\u30bb\u30c3\u30c8\u691c\u51fa",
         u"l_onset \u4ee5\u964d\u3067\u6700\u521d\u306b\u52d5\u7684\u95be\u5024\u3092\u8d85\u3048\u308b\u30b5\u30f3\u30d7\u30eb\u3092\u691c\u7d22\u3002"],
        ["5", u"\u30ec\u30a4\u30c6\u30f3\u30b7\u30fc\u8a08\u7b97",
         u"delta_n = r_onset - l_onset  |  latency_ms = delta_n / sample_rate * 1000"],
        ["6", u"\u7e70\u308a\u8fd4\u3057",
         u"\u8a2d\u5b9a\u8a66\u884c\u56de\u6570\uff081/3/10/30/100\uff09\u5206\u3001\u30a4\u30f3\u30bf\u30fc\u30d0\u30eb\u3092\u6311\u3093\u3067\u53cd\u5fa9\u3002"],
        ["7", u"\u7d71\u8a08\u51e6\u7406",
         u"Mean / Max / Min / \u6a19\u6e96\u5076\u5dee\u3092\u7b97\u51fa\u3002\u5e73\u5747\u5024\u6700\u8fd1\u508d\u306e\u6ce2\u5f62\u3092\u8868\u793a\u3002"],
    ], col_widths=[14 * mm, 34 * mm, 112 * mm], jp=True))

    # 6. 測定アルゴリズム詳細
    e.append(jsec(u"6. \u6e2c\u5b9a\u30a2\u30eb\u30b4\u30ea\u30ba\u30e0\u8a73\u7d30"))

    # 6.1 基準信号
    e.append(jh3(u"6.1  \u57fa\u6e96\u4fe1\u53f7\uff08L \u30c1\u30e3\u30f3\u30cd\u30eb\uff09"))
    e.append(b(u"\u6642\u9593\u5206\u89e3\u80fd\u3068\u30b9\u30da\u30af\u30c8\u30eb\u5e2f\u57df\u5e45\u306e\u30d0\u30e9\u30f3\u30b9\u3092\u53d6\u308b\u305f\u3081\u3001"
               u"\u30ac\u30a6\u30b9\u7a93\u30a4\u30f3\u30d1\u30eb\u30b9\u3092\u4f7f\u7528\u3057\u307e\u3059\u3002"
               u"\u3053\u308c\u306f\u30b9\u30e0\u30fc\u30ba\u306a\u5c71\u5f62\u3092\u6301\u3061\u307e\u3059\u3002"))
    e.append(mono(
        "click_len = max(int(sample_rate * 0.001), 8)\n"
        "t         = linspace(-3, 3, click_len)\n"
        "click     = exp(-t**2)\n"
        "click    /= max(abs(click))"))

    # 6.2 L チャンネル -- オンセット検出
    e.append(jh3(u"6.2  L \u30c1\u30e3\u30f3\u30cd\u30eb \u2014 \u30aa\u30f3\u30bb\u30c3\u30c8\u691c\u51fa"))
    e.append(b(u"\u7d04 0.5 ms \u306e\u7cfb\u7d71\u8aa4\u5dee\u3092\u76f8\u6bae\u3059\u308b\u305f\u3081\u3001"
               u"L/R \u4e21\u30c1\u30e3\u30f3\u30cd\u30eb\u3067\u540c\u69d8\u306e\u30aa\u30f3\u30bb\u30c3\u30c8\u691c\u51fa\u3092\u884c\u3044\u307e\u3059\uff1a"))
    e.append(mono(
        "l_onset = _find_onset(L_rec, noise_ref_end=noise_ref, search_start=0)"))
    e.append(b(u"\u3053\u306e l_onset \u304c DUT \u8a08\u6e2c\u306e\u6642\u9593\u57fa\u6e96\uff08t = 0.0 ms\uff09\u3068\u306a\u308a\u3001"
               u"\u6ce2\u5f62\u30d7\u30ed\u30c3\u30c8\u306e\u6a2a\u8f74\u306e\u539f\u70b9\u3068\u3057\u3066\u8a2d\u5b9a\u3055\u308c\u307e\u3059\u3002"))

    # 6.3 R チャンネル -- オンセット検出
    e.append(jh3(u"6.3  R \u30c1\u30e3\u30f3\u30cd\u30eb \u2014 \u30aa\u30f3\u30bb\u30c3\u30c8\u691c\u51fa"))
    e.append(b(u"DUT \u306e\u7279\u6027\u306b\u5fdc\u3058\u305f\u52d5\u7684\u306a\u95be\u5024\u3092\u4f7f\u7528\u3057\u3066\u30aa\u30f3\u30bb\u30c3\u30c8\u3092\u691c\u51fa\u3057\u307e\u3059\uff1a"))
    e.append(mono(
        "sig_peak  = max( abs( R_rec[l_onset:] ) )\n"
        "threshold = max(\n"
        "    noise_rms * 6.0,\n"
        "    sig_peak  * 0.01,\n"
        "    1e-5\n"
        ")\n"
        "r_onset = _find_onset(R_rec, threshold=threshold, search_start=l_onset)"))

    # 6.4 レイテンシー計算式
    e.append(jh3(u"6.4  \u30ec\u30a4\u30c6\u30f3\u30b7\u30fc\u8a08\u7b97\u5f0f"))
    e.append(b(u"L \u30aa\u30f3\u30bb\u30c3\u30c8\u3068 R \u30aa\u30f3\u30bb\u30c3\u30c8\u304c\u6c7a\u307e\u308c\u3070\u3001\u30ec\u30a4\u30c6\u30f3\u30b7\u30fc\u306e\u7b97\u51fa\u306f\u5358\u7d14\u3067\u3059\uff1a"))
    e.append(mono(
        "delta_n    = max(0, r_onset - l_onset)\n"
        "latency_ms = delta_n / sample_rate * 1000.0"))

    # 7. レベルチェック
    e.append(jsec(u"7. \u30ec\u30d9\u30eb\u30c1\u30a7\u30c3\u30af"))
    e.append(b(u"1 kHz \u30b5\u30a4\u30f3\u6ce2\uff08-12 dBFS\uff09\u3092 500 ms \u518d\u751f\u3057\u3001\u4e21\u30c1\u30e3\u30f3\u30cd\u30eb\u306e\u30d4\u30fc\u30af\u30ec\u30d9\u30eb\u3092\u8a08\u6e2c\u3057\u307e\u3059\uff1a"))
    e.append(make_table([
        [u"\u30ec\u30d9\u30eb\u7bc4\u56f2", u"\u5224\u5b9a", u"\u30ab\u30e9\u30fc", u"\u5bfe\u51e6"],
        [u"<= -36 dBFS", u"\u30ec\u30d9\u30eb\u5c0f / Low",  u"\u30aa\u30ec\u30f3\u30b8",
         u"\u51fa\u529b\u30ec\u30d9\u30eb\u307e\u305f\u306f\u5165\u529b\u30b2\u30a4\u30f3\u3092\u4e0a\u3052\u3066\u304f\u3060\u3055\u3044"],
        [u"-36 ~ -1 dBFS", u"\u9069\u6b63 / OK", u"\u30b0\u30ea\u30fc\u30f3",
         u"\u305d\u306e\u307e\u307e\u6e2c\u5b9a\u3092\u958b\u59cb\u3057\u3066\u304f\u3060\u3055\u3044"],
        [u">= -1 dBFS", u"\u30ec\u30d9\u30eb\u5927 / High", u"\u30ec\u30c3\u30c9",
         u"\u51fa\u529b\u30ec\u30d9\u30eb\u307e\u305f\u306f\u5165\u529b\u30b2\u30a4\u30f3\u3092\u4e0b\u3052\u3066\u304f\u3060\u3055\u3044"],
    ], col_widths=[30 * mm, 32 * mm, 20 * mm, 78 * mm], jp=True))

    # 8. 設定リファレンス
    e.append(jsec(u"8. \u8a2d\u5b9a\u30ea\u30d5\u30a1\u30ec\u30f3\u30b9"))
    e.append(make_table([
        [u"\u30d1\u30e9\u30e1\u30fc\u30bf\u30fc", u"\u9078\u629e\u80a2", u"\u30c7\u30d5\u30a9\u30eb\u30c8"],
        ["Device Name",   u"\u81ea\u7531\u5165\u529b",                              "Target_Device"],
        ["Input Device",  u"\u30b7\u30b9\u30c6\u30e0 \u30aa\u30fc\u30c7\u30a3\u30aa\u30c7\u30d0\u30a4\u30b9",
         u"\u30b7\u30b9\u30c6\u30e0\u30c7\u30d5\u30a9\u30eb\u30c8"],
        ["Output Device", u"\u30b7\u30b9\u30c6\u30e0 \u30aa\u30fc\u30c7\u30a3\u30aa\u30c7\u30d0\u30a4\u30b9",
         u"\u30b7\u30b9\u30c6\u30e0\u30c7\u30d5\u30a9\u30eb\u30c8"],
        ["Sample Rate",   "44100 / 48000 / 88200 / 96000 / 192000 Hz", "48000 Hz"],
        ["Trials",        "1 / 3 / 10 / 30 / 100",                    "10"],
        ["Interval",      u"0.5 / 1.0 / 2.0 / 5.0 \u79d2",           u"1.0 \u79d2"],
        ["Trigger",       "Auto (1%) / 3% / 5% / 10% / 20% / 30% (Peak %)", "Auto (1%)"],
    ], col_widths=[38 * mm, 90 * mm, 32 * mm], jp=True))

    return e


# ---------------------------------------------------------------------------
# Page background + footer
# ---------------------------------------------------------------------------
def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(C_NAVY)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    canvas.setFillColor(C_GRAY)
    canvas.setFont("Helvetica", 7)
    canvas.drawCentredString(
        W / 2, 10 * mm,
        "Dual-Channel RTL Analyzer  |  by ISAMU the Guitar  |  "
        "https://www.isamutheguitar.com  |  Page %d" % doc.page)
    canvas.restoreState()


# ---------------------------------------------------------------------------
# Build PDF
# ---------------------------------------------------------------------------
def build():
    doc = SimpleDocTemplate(
        OUT_PATH, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=18 * mm,
    )
    story = cover() + english() + japanese()
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print("\n  PDF saved to: %s\n" % OUT_PATH)


if __name__ == "__main__":
    build()
