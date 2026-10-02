"""Export this manuscript's bounded Typst subset to Springer Nature LaTeX."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]
OUT = PAPER / "natural-computing"
ABSTRACT_MIN = 150
ABSTRACT_MAX = 250

MATH = {
    "N times N": r"N\times N",
    "W = (q_1, ..., q_K)": r"W=(q_1,\ldots,q_K)",
    "P = (v_1, ..., v_L), quad L = |V|,": r"P=(v_1,\ldots,v_L),\quad L=|V|,",
    '"pos"_P(q_1) < "pos"_P(q_2) < ... < "pos"_P(q_K).': (
        r"\operatorname{pos}_P(q_1)<\operatorname{pos}_P(q_2)<\cdots<\operatorname{pos}_P(q_K)."
    ),
    'eta(e) = product_j "softplus"(h_j(e))^(gamma_j),': r"\eta(e)=\prod_j\operatorname{softplus}(h_j(e))^{\gamma_j},",
    "ell(e) = alpha tau_e + beta log eta(e),": r"\ell(e)=\alpha\tau_e+\beta\log\eta(e),",
    'f = L_P + beta_1 k_P + beta_2/(1+d_M) + beta_3 I_("solved"),': (
        r"f=L_P+\beta_1 k_P+\frac{\beta_2}{1+d_M}+\beta_3 I_{\mathrm{solved}},"
    ),
    "r in {1,...,n}": r"r\in\{1,\ldots,n\}",
    "w_r = (n - 2r + 1)/(n - 1).": r"w_r=\frac{n-2r+1}{n-1}.",
    "tilde(tau)_e = v_c(t) tau_e + v_b(t) D_e,": r"\widetilde{\tau}_e=v_c(t)\tau_e+v_b(t)D_e,",
    "v_b(t)=tanh(1-t/T)": r"v_b(t)=\tanh(1-t/T)",
    "cal(N)(0, (tau_max/4)^2)": r"\mathcal{N}(0,(\tau_{\max}/4)^2)",
    "Delta = 1/150 sum_(p=1)^150 (s_F(p) - s_0(p)).": r"\Delta=\frac{1}{150}\sum_{p=1}^{150}\bigl(s_F(p)-s_0(p)\bigr).",
    "floor(0.025B)": r"\lfloor0.025B\rfloor",
    "ceil(0.975B)-1": r"\lceil0.975B\rceil-1",
}


def math(value: str) -> str:
    value = value.strip()
    if value in MATH:
        return MATH[value]
    value = re.sub(r'gamma_\("(\w+)"\)', r"\\gamma_{\\mathrm{\1}}", value)
    value = value.replace("tau_max", r"\tau_{\max}")
    value = re.sub(r"(?<![A-Za-z\\])(alpha|beta|tau)(?![A-Za-z])", r"\\\1", value)
    if re.search(r'\b(times|product|sum|floor|ceil|cal|tilde)\b|"|\.\.\.', value):
        raise ValueError(f"Unmapped Typst math: {value}")
    return value


def text(value: str) -> str:
    saved: list[str] = []

    def hold(latex: str) -> str:
        saved.append(latex)
        return f"ZZTOKEN{len(saved)-1}ZZ"

    value = re.sub(r"#footnote\[([^\]]+)\]", lambda m: hold(r"\footnote{" + text(m[1]) + "}"), value)
    value = re.sub(r'#raw\("([^"]+)"\)', lambda m: hold(r"\path{" + m[1] + "}"), value)
    value = re.sub(r'#link\("([^"]+)"\)', lambda m: hold(r"\url{" + m[1] + "}"), value)
    value = re.sub(r"\$([^$]+)\$", lambda m: hold("$" + math(m[1]) + "$"), value)
    value = re.sub(r"\*([^*]+)\*", lambda m: hold(r"\textbf{" + text(m[1]) + "}"), value)
    value = re.sub(r"_([^_]+)_", lambda m: hold(r"\emph{" + text(m[1]) + "}"), value)

    def cite(match: re.Match[str]) -> str:
        key = match[1]
        if key.startswith(("tab-", "fig-")):
            kind = "Table" if key.startswith("tab-") else "Fig."
            return hold(kind + r"~\ref{" + key + "}")
        return hold(r"\citep{" + key + "}")

    value = re.sub(r"@([A-Za-z][A-Za-z0-9_-]+)", cite, value)
    for old, new in {
        "%": r"\%",
        "&": r"\&",
        "#": r"\#",
        "±": r"\(\pm\)",
        "\N{MINUS SIGN}": r"\(-\)",
        "\N{MULTIPLICATION SIGN}": r"\(\times\)",
        "\N{EN DASH}": "--",
        "—": "---",
        "“": "``",
        "”": "''",
        "\N{RIGHT SINGLE QUOTATION MARK}": "'",
        "ã": r"\~{a}",
        "ç": r"\c{c}",
        "í": r"\'{i}",
        "ó": r"\'{o}",
        "é": r"\'{e}",
    }.items():
        value = value.replace(old, new)
    for i, item in enumerate(saved):
        value = value.replace(f"ZZTOKEN{i}ZZ", item)
    return value


def figure(block: str) -> str:
    label = re.search(r"\) <([^>]+)>$", block).group(1)
    caption = text(re.search(r"caption: \[(.*)\],\n\)", block, re.S).group(1)).rstrip(".")
    if "image(" in block:
        source = re.search(r'image\("([^"]+)"', block).group(1)
        name = "Fig1" if label == "fig-primary" else "Fig2"
        svg = (PAPER / source).read_text()
        svg = re.sub(r'<text[^>]*class="(?:title|subtitle|note)"[^>]*>.*?</text>\n?', "", svg)
        svg = svg.replace("font-size: 13px", "font-size: 24px").replace("font-size: 12px", "font-size: 24px")
        svg = svg.replace('viewBox="0 0 1040 560"', 'viewBox="0 110 1040 440"')
        svg = svg.replace('viewBox="0 0 940 560"', 'viewBox="0 110 940 420"')
        svg = svg.replace('height="560"', 'height="440"' if name == "Fig1" else 'height="420"')
        svg_path = OUT / f"{name}.svg"
        svg_path.write_text(svg)
        converter = shutil.which("rsvg-convert")
        if converter is None:
            raise SystemExit("Install librsvg (rsvg-convert) to export vector figures")
        for extension, fmt in [("pdf", "pdf"), ("eps", "eps")]:
            subprocess.run(  # noqa: S603 -- local manuscript paths, no shell
                [converter, "--format", fmt, "--output", str(OUT / f"{name}.{extension}"), str(svg_path)],
                check=True,
            )
        return "\n".join(
            [
                r"\begin{figure}[htbp]",
                r"\centering",
                r"\includegraphics[width=\textwidth]{" + name + ".pdf}",
                r"\caption{" + caption + r"}\label{" + label + "}",
                r"\end{figure}",
            ]
        )
    rows = []
    for line in block.splitlines():
        if line.strip().startswith(("table.header(", "[")):
            cells = re.findall(r"\[([^\]]+)\]", line)
            rows.append(" & ".join(text(c) for c in cells) + r" \\")
    columns = "lrlr" if label == "tab-config" else "lrrr"
    return "\n".join(
        [
            r"\begin{table}[htbp]",
            r"\centering",
            r"\caption{" + caption + r"}\label{" + label + "}",
            r"\begin{tabular}{" + columns + "}",
            r"\toprule",
            rows[0],
            r"\midrule",
            *rows[1:],
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table}",
        ]
    )


def export() -> None:
    source = (PAPER / "main.typ").read_text()
    abstract = source.split("*Abstract.*", 1)[1].split("\n]", 1)[0].strip()
    if not ABSTRACT_MIN <= len(abstract.split()) <= ABSTRACT_MAX:
        raise ValueError("Abstract outside Natural Computing word limit")
    body = "= Introduction" + source.split("= Introduction", 1)[1]
    body = body.split("#bibliography(", 1)[0].strip()
    figures: dict[str, str] = {}

    def store(match: re.Match[str]) -> str:
        key = f"FIGUREBLOCK{len(figures)}"
        figures[key] = figure(match[0])
        return key

    body = re.sub(r"#figure\(.*?\) <[^>]+>", store, body, flags=re.S)
    blocks = []
    for raw_block in body.split("\n\n"):
        block = raw_block.strip()
        if not block:
            continue
        if block in figures:
            blocks.append(figures[block])
        elif block.startswith("== "):
            blocks.append(r"\subsection{" + text(block[3:]) + "}")
        elif block.startswith("= "):
            blocks.append(r"\section{" + text(block[2:]) + "}")
        elif block.startswith("+ "):
            blocks.append(
                "\n".join(
                    [
                        r"\begin{enumerate}",
                        *(r"\item " + text(line[2:]) for line in block.splitlines()),
                        r"\end{enumerate}",
                    ]
                )
            )
        elif block.startswith("$ ") and block.endswith(" $"):
            blocks.append(r"\begin{equation}" + "\n" + math(block[1:-1]) + "\n" + r"\end{equation}")
        else:
            blocks.append(text(block))
    preamble = (OUT / "preamble.tex.in").read_text()
    result = preamble.replace("@@ABSTRACT@@", text(" ".join(abstract.split())))
    result += "\n\n".join(blocks) + "\n\n\\bibliography{references}\n\\end{document}\n"
    if re.search(r"#(?:raw|link|figure|footnote)|(?<![A-Za-z0-9.])@[A-Za-z]|ZZTOKEN|FIGUREBLOCK", result):
        raise ValueError("Unconverted source markup")
    (OUT / "main.tex").write_text(result)
    shutil.copyfile(PAPER / "references.bib", OUT / "references.bib")
    print(f"Exported Natural Computing manuscript; abstract: {len(abstract.split())} words")


if __name__ == "__main__":
    export()
