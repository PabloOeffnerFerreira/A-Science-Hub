import os
import time

def export_figure(fig, out_dir="storage/images", dpi=150):
    os.makedirs(out_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(out_dir, f"image_{ts}.png")
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    return path
