"""Manual diagnostic: loads the trained models and runs each analyzer once.

Windows:  python ml\\scripts\\check_inference.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.inference import (InvalidInputError, analyze_email, analyze_qr_payload,  # noqa: E402
                          analyze_text, analyze_url, model_status)

FAILURES = []


def run(label, fn, *args, **kwargs):
    try:
        r = fn(*args, **kwargs)
        json.dumps(r)  # raises TypeError if anything is not JSON-serializable
    except Exception as e:  # noqa: BLE001
        FAILURES.append(label)
        print(f"[FAIL] {label}: {type(e).__name__}: {e}")
        return None
    print(f"[ OK ] {label}")
    return r


def show(r):
    if not r:
        return
    print(f"       classification={r['classification']} risk={r['risk_score']} severity={r['severity']} "
          f"confidence={r['confidence']} model_used={r['model_used']} version={r['model_version']}")
    print(f"       indicators={[i['code'] for i in r['indicators']]}")
    print(f"       model_features={[f['feature'] for f in r['explanation']['model_features'][:5]]}")


def expect_error(label, fn, *args):
    try:
        fn(*args)
    except InvalidInputError as e:
        print(f"[ OK ] {label} -> InvalidInputError: {e}")
    except Exception as e:  # noqa: BLE001
        FAILURES.append(label)
        print(f"[FAIL] {label} raised {type(e).__name__} instead of InvalidInputError")
    else:
        FAILURES.append(label)
        print(f"[FAIL] {label} did not raise")


print("=== model_status ===")
st = run("model_status()", model_status)
if st:
    print(json.dumps(st, indent=2)[:1500])
    if not st["text_model"] or not st["url_model"]:
        print("!! A model failed to load (see mode above). Check ml\\models\\text_model and url_model.")

print("\n=== analyzers ===")
show(run("analyze_text(normal)", analyze_text, "Hi team, the agenda for Thursday's meeting is attached."))
show(run("analyze_text(suspicious)", analyze_text,
         "URGENT: Your account will be suspended within 24 hours. Verify your password now at http://paypa1-secure.xyz/login"))
show(run("analyze_url(legit)", analyze_url, "https://example.com"))
show(run("analyze_url(suspicious)", analyze_url, "http://paypa1-secure-login.xyz/verify/account"))
show(run("analyze_email", analyze_email, subject="Verify your account",
         body="Your account will be locked. Confirm your password: http://192.168.1.5/login",
         sender="PayPal Support <help@gmail.com>"))
show(run("analyze_qr_payload(url)", analyze_qr_payload, "http://paypa1-secure-login.xyz/verify"))
show(run("analyze_qr_payload(text)", analyze_qr_payload, "Your account will be suspended. Verify your password now."))
show(run("analyze_qr_payload(upi)", analyze_qr_payload, "upi://pay?pa=shop@okaxis&pn=Shop&am=250&cu=INR"))

print("\n=== invalid input (must be clean errors, not tracebacks) ===")
expect_error("analyze_text('')", analyze_text, "")
expect_error("analyze_url(None)", analyze_url, None)
expect_error("analyze_qr_payload('  ')", analyze_qr_payload, "  ")
expect_error("analyze_email(empty)", analyze_email, "", "")

print("\nRESULT:", "ALL CHECKS PASSED" if not FAILURES else f"{len(FAILURES)} FAILED: {FAILURES}")
sys.exit(1 if FAILURES else 0)