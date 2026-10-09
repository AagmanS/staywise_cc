"""Quick end-to-end test of the /predict endpoint."""
import urllib.request, json, time

API = "http://localhost:5000/predict"

def test(label, payload):
    data = json.dumps(payload).encode()
    req  = urllib.request.Request(API, data=data,
                                  headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req) as resp:
        r = json.loads(resp.read())
    elapsed = time.time() - t0

    print(f"\n{'='*55}")
    print(f"  {label}  ({elapsed:.2f}s)")
    print(f"{'='*55}")
    print(f"  Probability : {r['probability_pct']}%")
    print(f"  Risk level  : {r['risk_level']}")
    print(f"  Churn flag  : {r['churn']}")
    print("  Risk factors:")
    for f in r["risk_factors"]:
        bar = "█" * (f["bar_pct"] // 10)
        print(f"    {f['label']:22} {bar:10} [{f['impact']:8}] = {f['value_label']}")
    print("  Protective factors:")
    for f in r["protective_factors"]:
        bar = "█" * (f["bar_pct"] // 10)
        print(f"    {f['label']:22} {bar:10} [{f['impact']:8}] = {f['value_label']}")
    print(f"  Rec[0]: {r['recommendations'][0][:70]}")
    assert "probability" in r
    assert "risk_factors" in r
    assert "protective_factors" in r
    print("  ✓ All assertions passed")


# ── Test 1: High-risk customer ────────────────────────────────────────────────
test("HIGH-RISK SAMPLE", {
    "gender": "Male", "senior_citizen": "0", "partner": "No", "dependents": "No",
    "tenure_months": "3", "phone_service": "Yes", "multiple_lines": "No",
    "internet_service": "Fiber optic", "online_security": "No", "online_backup": "No",
    "device_protection": "No", "tech_support": "No", "streaming_tv": "Yes",
    "streaming_movies": "Yes", "contract": "Month-to-month", "paperless_billing": "Yes",
    "payment_method": "Electronic check", "monthly_charges": "95.70",
    "total_charges": "287.10",
})

# ── Test 2: Low-risk customer ─────────────────────────────────────────────────
test("LOW-RISK SAMPLE", {
    "gender": "Female", "senior_citizen": "0", "partner": "Yes", "dependents": "Yes",
    "tenure_months": "60", "phone_service": "Yes", "multiple_lines": "Yes",
    "internet_service": "DSL", "online_security": "Yes", "online_backup": "Yes",
    "device_protection": "Yes", "tech_support": "Yes", "streaming_tv": "No",
    "streaming_movies": "No", "contract": "Two year", "paperless_billing": "No",
    "payment_method": "Bank transfer (automatic)", "monthly_charges": "65.40",
    "total_charges": "3924.00",
})

# ── Test 3: Validation — missing field ───────────────────────────────────────
import urllib.error
try:
    data = json.dumps({"gender": "Male"}).encode()
    req  = urllib.request.Request(API, data=data,
                                  headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        r = json.loads(resp.read())
    print("\n✗ Expected 400 for missing fields but got 200")
except urllib.error.HTTPError as e:
    if e.code == 400:
        body = json.loads(e.read())
        print(f"\n  Validation test ✓  →  400: {body['error'][:60]}")
    else:
        print(f"\n  Unexpected status {e.code}")

print("\n✓ All tests complete\n")
