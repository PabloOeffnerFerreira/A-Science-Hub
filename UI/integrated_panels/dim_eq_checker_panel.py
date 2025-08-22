from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QSizePolicy
from PyQt6.QtCore import Qt

class DimensionalEquationChecker(QWidget):
    def __init__(self):
        super().__init__()

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedSize(360, 180)

        self._dims = self._unit_dims()
        self._prefixes = {"Y","Z","E","P","T","G","M","k","h","da","d","c","m","μ","u","n","p","f","a","z","y"}

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(4)

        form = QFormLayout()
        form.setHorizontalSpacing(6)
        form.setVerticalSpacing(2)

        self.left = QLineEdit()
        self.left.setPlaceholderText("Left (e.g. N)")
        self.left.setFixedHeight(20)

        self.right = QLineEdit()
        self.right.setPlaceholderText("Right (e.g. kg*m/s^2)")
        self.right.setFixedHeight(20)

        self.status = QLineEdit()
        self.status.setReadOnly(True)
        self.status.setFixedHeight(20)

        self.detail = QLabel("")
        self.detail.setWordWrap(True)
        self.detail.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        form.addRow(self._lbl("Left"), self.left)
        form.addRow(self._lbl("Right"), self.right)
        form.addRow(self._lbl("Result"), self.status)
        form.addRow(self._lbl("Detail"), self.detail)

        root.addLayout(form)

        self.left.textEdited.connect(self._recompute)
        self.right.textEdited.connect(self._recompute)

    def _lbl(self, t):
        l = QLabel(t); l.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter); return l

    def _unit_dims(self):
        L,M,T,I,Th,N,Ju = "L","M","T","I","Θ","N","J"
        def v(**k): return k
        d = {
            "m": v(L=1), "kg": v(M=1), "g": v(M=1), "s": v(T=1), "A": v(I=1), "K": v(Th=1), "mol": v(N=1), "cd": v(Ju=1),
            "Hz": v(T=-1),
            "N": v(M=1, L=1, T=-2),
            "Pa": v(M=1, L=-1, T=-2),
            "J": v(M=1, L=2, T=-2),
            "W": v(M=1, L=2, T=-3),
            "C": v(T=1, I=1),
            "V": v(M=1, L=2, T=-3, I=-1),
            "Ω": v(M=1, L=2, T=-3, I=-2),
            "ohm": v(M=1, L=2, T=-3, I=-2),
            "S": v(M=-1, L=-2, T=3, I=2),
            "F": v(M=-1, L=-2, T=4, I=2),
            "T": v(M=1, T=-2, I=-1),
            "H": v(M=1, L=2, T=-2, I=-2),
            "Wb": v(M=1, L=2, T=-2, I=-1),
            "lm": v(Ju=1),
            "lx": v(Ju=1, L=-2),
            # convenience composites
            "min": v(T=1), "h": v(T=1),
        }
        return d

    def _recompute(self, *_):
        ltxt = self.left.text().strip()
        rtxt = self.right.text().strip()
        if not ltxt or not rtxt:
            self.status.clear(); self.detail.clear(); return
        try:
            ldim = self._dim_of_expr(ltxt)
            rdim = self._dim_of_expr(rtxt)
        except Exception as e:
            self.status.setText("Error")
            self.detail.setText(str(e))
            return
        if self._equal_dims(ldim, rdim):
            self.status.setText("OK (dimensions match)")
        else:
            self.status.setText("Mismatch")
        self.detail.setText(f"L: {self._fmt(ldim)}   R: {self._fmt(rdim)}")

    def _fmt(self, d):
        if not d: return "dimensionless (1)"
        parts = []
        for k in ("M","L","T","I","Θ","N","J"):
            if k in d and d[k] != 0:
                parts.append(f"{k}^{d[k]}")
        return " · ".join(parts) if parts else "dimensionless (1)"

    def _equal_dims(self, a, b):
        keys = set(a.keys()) | set(b.keys())
        for k in keys:
            if a.get(k,0) != b.get(k,0): return False
        return True

    def _dim_of_expr(self, s):
        self._tokens = self._tokenize(s)
        self._pos = 0
        dim = self._parse_expr()
        if self._pos != len(self._tokens):
            raise ValueError("Unexpected token near end")
        return dim

    def _tokenize(self, s):
        out = []
        i = 0
        while i < len(s):
            c = s[i]
            if c.isspace():
                i += 1; continue
            if c in "*/()^=+":
                out.append(c); i += 1; continue
            if c.isdigit() or c=='.':
                j=i
                while j<len(s) and (s[j].isdigit() or s[j]=='.'):
                    j+=1
                out.append(("NUM", s[i:j])); i=j; continue
            j=i
            while j<len(s) and (s[j].isalnum() or s[j] in ["μ","Ω","_"]):
                j+=1
            if j>i:
                out.append(("SYM", s[i:j])); i=j; continue
            # 🚨 catch-all for bad characters:
            raise ValueError(f"Invalid character: {s[i]}")
        return out


    def _parse_expr(self):
        d = self._parse_term()
        while self._pos < len(self._tokens) and self._tokens[self._pos] in ("*","/"):
            op = self._tokens[self._pos]; self._pos += 1
            t = self._parse_term()
            d = self._combine(d, t, 1 if op=="*" else -1)
        if self._pos < len(self._tokens) and self._tokens[self._pos] == "=":
            self._pos += 1
            r = self._parse_expr()
            return self._combine(d, r, -1)
        return d

    def _parse_term(self):
        d = self._parse_factor()
        if self._pos < len(self._tokens) and self._tokens[self._pos] == "^":
            self._pos += 1
            exp_tok = self._tokens[self._pos]; self._pos += 1
            if isinstance(exp_tok, tuple) and exp_tok[0]=="NUM":
                e = int(float(exp_tok[1]))
            else:
                raise ValueError("Exponent must be a number")
            d = self._pow(d, e)
        return d

    def _parse_factor(self):
        if self._pos >= len(self._tokens):
            raise ValueError("Unexpected end")
        tok = self._tokens[self._pos]; self._pos += 1
        if tok == "(":
            d = self._parse_expr()
            if self._pos >= len(self._tokens) or self._tokens[self._pos] != ")":
                raise ValueError("Missing ')'")
            self._pos += 1
            return d
        if isinstance(tok, tuple) and tok[0]=="NUM":
            return {}
        if isinstance(tok, tuple) and tok[0]=="SYM":
            return self._unit_dim_from_symbol(tok[1])
        raise ValueError("Unexpected token")

    def _unit_dim_from_symbol(self, sym):
        s = sym
        if s in self._dims:
            return dict(self._dims[s])
        if len(s) >= 2:
            if s[:2] in {"da"} and s[2:] in self._dims:
                return dict(self._dims[s[2:]])
            if s[0] in self._prefixes and s[1:] in self._dims:
                return dict(self._dims[s[1:]])
        if s.endswith("g") and s != "kg":
            return dict(self._dims.get("g", {}))
        raise ValueError(f"Unknown unit: {sym}")

    def _combine(self, a, b, sign):
        out = dict(a)
        for k,v in b.items():
            out[k] = out.get(k,0) + sign*v
            if out[k] == 0: del out[k]
        return out

    def _pow(self, a, e):
        return {k: v*e for k,v in a.items()}
