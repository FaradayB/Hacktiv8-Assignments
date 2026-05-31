"""
=============================================================================
 Vehicle Predictive Maintenance — ML Classification Pipeline
=============================================================================
 System Architecture (from Flow Diagram):
   Vehicle Sensors & OBD
       → IoT Layer (1–2 hr intervals, 7 AM–7 PM)
       → Central Database
           ├── Track 1 (Workshop/Mechanic):  ML Anomaly Detection (30-day)
           │       → If Anomaly → LLM + RAG → Technician Fault Brief
           └── Track 2 (Vehicle Owner):     Risk Level Detection (12-hr)
                   → If Risk → LLM Summarizer (Bahasa Indonesia) → Push Alert

 Track 1 — Fault Classification (8 classes)
   0: Normal            1: Battery Degradation   2: Brake System Issue
   3: Cooling Problem   4: Engine Misfire         5: Alternator Failure
   6: Oil Pressure Issue  7: Transmission Problem

 Track 2 — Risk Detection (4 classes)
   0: No Risk   1: Low Risk   2: Medium Risk   3: High Risk
=============================================================================
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    classification_report, confusion_matrix,
    accuracy_score, f1_score, ConfusionMatrixDisplay
)

# Classifiers
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

import joblib
import os

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

DATA_PATH   = "/mnt/user-data/uploads/Vehicle_Sensor_Dataset_v2.xlsx"
OUTPUT_DIR  = "/mnt/user-data/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

RANDOM_STATE = 42
TEST_SIZE    = 0.2
CV_FOLDS     = 5

# Track 1 features (30-day telemetry window)
TRACK1_FEATURES = [
    "O2 SENSOR V", "MAF G PER S", "THROTTLE POS PCT",
    "CRANK RPM", "CAM ADVANCE DEG", "KNOCK COUNT 30D",
    "COOLANT TEMP C", "OIL PRESSURE PSI", "MAP KPA",
    "EGR DUTY PCT", "BATTERY VOLTAGE V", "FUEL TEMP C"
]
TRACK1_TARGET  = "FAULT CLASS"
TRACK1_LABELS  = [
    "Normal", "Battery Degradation", "Brake System Issue",
    "Cooling System Problem", "Engine Misfire", "Alternator Failure",
    "Oil Pressure Issue", "Transmission Problem"
]

# Track 2 features (12-hr daily window)
TRACK2_FEATURES = [
    "O2 SENSOR V", "MAF G PER S", "THROTTLE POS PCT",
    "COOLANT TEMP C", "OIL PRESSURE PSI", "BATTERY VOLTAGE V",
    "TPMS PSI", "AMBIENT TEMP C", "CABIN HUMIDITY PCT",
    "FUEL LEVEL PCT", "BRAKE PEDAL EVENTS", "SPEED KMH"
]
TRACK2_TARGET  = "RISK CLASS"
TRACK2_LABELS  = ["No Risk", "Low Risk", "Medium Risk", "High Risk"]

# ─────────────────────────────────────────────────────────────────────────────
# COLOUR PALETTE
# ─────────────────────────────────────────────────────────────────────────────

TRACK1_COLOURS = [
    "#4CAF50", "#2196F3", "#FF5722", "#FF9800",
    "#E91E63", "#9C27B0", "#795548", "#00BCD4"
]
TRACK2_COLOURS = ["#4CAF50", "#FFC107", "#FF9800", "#F44336"]

RISK_EMOJIS = {0: "🟢", 1: "🟡", 2: "🟠", 3: "🔴"}
RISK_ACTIONS = {
    0: "No action needed.",
    1: "Monitor — minor deviations detected.",
    2: "Schedule a workshop visit soon.",
    3: "⚠️  Immediate inspection required!"
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPER UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def load_data():
    xl = pd.ExcelFile(DATA_PATH)
    t1 = xl.parse("Track1_Technician_30Day")
    t2 = xl.parse("Track2_Owner_12Hr")
    print(f"  Track 1 loaded: {t1.shape[0]:,} rows × {t1.shape[1]} cols")
    print(f"  Track 2 loaded: {t2.shape[0]:,} rows × {t2.shape[1]} cols")
    return t1, t2


def prepare_split(df, features, target):
    X = df[features].values
    y = df[target].values
    return train_test_split(X, y, test_size=TEST_SIZE,
                            random_state=RANDOM_STATE, stratify=y)


def build_pipeline(clf):
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf",    clf)
    ])


def evaluate(pipe, X_train, X_test, y_train, y_test, labels):
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    acc    = accuracy_score(y_test, y_pred)
    f1     = f1_score(y_test, y_pred, average="weighted")
    return acc, f1, y_pred


def cv_score(pipe, X, y):
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    scores = cross_val_score(pipe, X, y, cv=cv, scoring="f1_weighted", n_jobs=-1)
    return scores.mean(), scores.std()


# ─────────────────────────────────────────────────────────────────────────────
# CANDIDATE MODELS
# ─────────────────────────────────────────────────────────────────────────────

def get_candidate_models():
    return {
        "Random Forest":        RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE, n_jobs=-1),
        "Gradient Boosting":    GradientBoostingClassifier(n_estimators=200, random_state=RANDOM_STATE),
        "Logistic Regression":  LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        "SVM (RBF)":            SVC(kernel="rbf", probability=True, random_state=RANDOM_STATE),
        "K-Nearest Neighbours": KNeighborsClassifier(n_neighbors=7),
    }


# ─────────────────────────────────────────────────────────────────────────────
# PLOTTING HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def plot_confusion_matrix(cm, labels, title, ax, colours):
    n = len(labels)
    im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
    ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
    tick_marks = np.arange(n)
    short = [l.replace(" ", "\n") for l in labels]
    ax.set_xticks(tick_marks); ax.set_xticklabels(short, fontsize=7.5)
    ax.set_yticks(tick_marks); ax.set_yticklabels(short, fontsize=7.5)
    ax.set_xlabel("Predicted", fontsize=9)
    ax.set_ylabel("Actual",    fontsize=9)
    thresh = cm.max() / 2
    for i in range(n):
        for j in range(n):
            ax.text(j, i, str(cm[i, j]),
                    ha="center", va="center", fontsize=8,
                    color="white" if cm[i, j] > thresh else "black")


def plot_feature_importance(pipe, feature_names, title, ax, colours):
    clf = pipe.named_steps["clf"]
    if not hasattr(clf, "feature_importances_"):
        ax.text(0.5, 0.5, "Feature importance\nnot available for this model",
                ha="center", va="center", transform=ax.transAxes, fontsize=10)
        return
    imp = clf.feature_importances_
    idx = np.argsort(imp)
    ax.barh([feature_names[i] for i in idx], imp[idx],
            color=colours[0], alpha=0.85, edgecolor="white")
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_xlabel("Importance", fontsize=9)
    ax.tick_params(axis="y", labelsize=8)
    ax.spines[["top", "right"]].set_visible(False)


# ─────────────────────────────────────────────────────────────────────────────
# TRACK RUNNER
# ─────────────────────────────────────────────────────────────────────────────

def run_track(track_name, df, features, target, labels, colours):
    print(f"\n{'='*60}")
    print(f"  {track_name}")
    print(f"{'='*60}")

    X_train, X_test, y_train, y_test = prepare_split(df, features, target)
    X_all = df[features].values
    y_all = df[target].values

    print(f"  Train: {len(X_train):,}   Test: {len(X_test):,}")
    print(f"  Classes: {len(labels)}")

    models = get_candidate_models()
    results = {}

    print(f"\n  {'Model':<25} {'Test Acc':>9} {'F1-W':>7} {'CV F1 Mean':>11} {'CV Std':>8}")
    print("  " + "-"*65)

    for name, clf in models.items():
        pipe          = build_pipeline(clf)
        acc, f1, _    = evaluate(pipe, X_train, X_test, y_train, y_test, labels)
        cv_mean, cv_s = cv_score(build_pipeline(clf), X_all, y_all)
        results[name] = {"acc": acc, "f1": f1, "cv_mean": cv_mean, "cv_std": cv_s, "pipe": pipe}
        print(f"  {name:<25} {acc:>9.4f} {f1:>7.4f} {cv_mean:>11.4f} {cv_s:>8.4f}")

    # ── Best model ──
    best_name = max(results, key=lambda k: results[k]["cv_mean"])
    best      = results[best_name]
    best_pipe = best["pipe"]

    print(f"\n  ✅  Best model: {best_name}  (CV F1 = {best['cv_mean']:.4f} ± {best['cv_std']:.4f})")

    # Re-fit best on full train for final predictions
    best_pipe.fit(X_train, y_train)
    y_pred = best_pipe.predict(X_test)

    print(f"\n  Classification Report:\n")
    print(classification_report(y_test, y_pred,
                                target_names=labels, digits=4, zero_division=0))

    cm = confusion_matrix(y_test, y_pred)
    return {
        "results": results, "best_name": best_name, "best_pipe": best_pipe,
        "cm": cm, "y_test": y_test, "y_pred": y_pred,
        "X_train": X_train, "X_test": X_test, "y_train": y_train,
        "features": features, "labels": labels, "colours": colours
    }


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 1 — MODEL COMPARISON BAR CHARTS
# ─────────────────────────────────────────────────────────────────────────────

def fig_model_comparison(t1_out, t2_out):
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    fig.suptitle("Vehicle Predictive Maintenance — Model Comparison",
                 fontsize=14, fontweight="bold", y=1.01)

    for ax, out, title in [
        (axes[0], t1_out, "Track 1 — Fault Classification (Technician)"),
        (axes[1], t2_out, "Track 2 — Risk Detection (Owner)"),
    ]:
        names   = list(out["results"].keys())
        cv_means = [out["results"][n]["cv_mean"] for n in names]
        cv_stds  = [out["results"][n]["cv_std"]  for n in names]
        test_acc = [out["results"][n]["acc"]      for n in names]

        x = np.arange(len(names))
        w = 0.35
        bars1 = ax.bar(x - w/2, cv_means, w, yerr=cv_stds, capsize=4,
                       color="#1565C0", alpha=0.85, label="CV F1 (Weighted)")
        bars2 = ax.bar(x + w/2, test_acc, w,
                       color="#43A047", alpha=0.85, label="Test Accuracy")

        ax.set_xticks(x)
        ax.set_xticklabels([n.replace(" ", "\n") for n in names], fontsize=8)
        ax.set_ylim(0, 1.05)
        ax.set_ylabel("Score", fontsize=9)
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.legend(fontsize=8)
        ax.spines[["top", "right"]].set_visible(False)

        # Highlight best
        best_idx = names.index(out["best_name"])
        bars1[best_idx].set_edgecolor("gold"); bars1[best_idx].set_linewidth(2.5)
        bars2[best_idx].set_edgecolor("gold"); bars2[best_idx].set_linewidth(2.5)
        ax.annotate("★ Best", xy=(x[best_idx], max(cv_means[best_idx], test_acc[best_idx]) + 0.02),
                    ha="center", fontsize=8, color="darkgoldenrod", fontweight="bold")

    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig1_model_comparison.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\n  Saved → {path}")
    return path


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 2 — CONFUSION MATRICES & FEATURE IMPORTANCE
# ─────────────────────────────────────────────────────────────────────────────

def fig_confusion_and_importance(t1_out, t2_out):
    fig = plt.figure(figsize=(20, 10))
    fig.suptitle("Confusion Matrices & Feature Importance — Best Models",
                 fontsize=14, fontweight="bold")

    gs = gridspec.GridSpec(2, 3, figure=fig, wspace=0.35, hspace=0.45)

    ax_cm1  = fig.add_subplot(gs[0, :2])
    ax_fi1  = fig.add_subplot(gs[0, 2])
    ax_cm2  = fig.add_subplot(gs[1, :2])
    ax_fi2  = fig.add_subplot(gs[1, 2])

    plot_confusion_matrix(
        t1_out["cm"], t1_out["labels"],
        f"Track 1 — {t1_out['best_name']}\nFault Classification (8 Classes)",
        ax_cm1, t1_out["colours"]
    )
    plot_feature_importance(
        t1_out["best_pipe"], t1_out["features"],
        "Track 1 — Feature Importance", ax_fi1, t1_out["colours"]
    )
    plot_confusion_matrix(
        t2_out["cm"], t2_out["labels"],
        f"Track 2 — {t2_out['best_name']}\nRisk Detection (4 Classes)",
        ax_cm2, t2_out["colours"]
    )
    plot_feature_importance(
        t2_out["best_pipe"], t2_out["features"],
        "Track 2 — Feature Importance", ax_fi2, t2_out["colours"]
    )

    path = os.path.join(OUTPUT_DIR, "fig2_confusion_importance.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved → {path}")
    return path


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 3 — SENSOR DISTRIBUTION BY CLASS
# ─────────────────────────────────────────────────────────────────────────────

def fig_sensor_distributions(df1, df2):
    # Track 1: show 4 key sensors
    t1_sensors = ["BATTERY VOLTAGE V", "COOLANT TEMP C", "OIL PRESSURE PSI", "CRANK RPM"]
    # Track 2: show 4 key sensors
    t2_sensors = ["BATTERY VOLTAGE V", "COOLANT TEMP C", "TPMS PSI", "SPEED KMH"]

    fig, axes = plt.subplots(2, 4, figsize=(20, 8))
    fig.suptitle("Key Sensor Distributions by Class",
                 fontsize=14, fontweight="bold")

    for i, col in enumerate(t1_sensors):
        ax = axes[0, i]
        for cls_id, label in enumerate(TRACK1_LABELS):
            data = df1.loc[df1[TRACK1_TARGET] == cls_id, col]
            ax.hist(data, bins=20, alpha=0.55, label=label,
                    color=TRACK1_COLOURS[cls_id], density=True)
        ax.set_title(f"T1 · {col}", fontsize=9, fontweight="bold")
        ax.set_xlabel(col, fontsize=7)
        ax.set_ylabel("Density", fontsize=7)
        ax.tick_params(labelsize=7)
        ax.spines[["top", "right"]].set_visible(False)
        if i == 3:
            ax.legend(fontsize=5.5, loc="upper right")

    for i, col in enumerate(t2_sensors):
        ax = axes[1, i]
        for cls_id, label in enumerate(TRACK2_LABELS):
            data = df2.loc[df2[TRACK2_TARGET] == cls_id, col]
            ax.hist(data, bins=20, alpha=0.55, label=label,
                    color=TRACK2_COLOURS[cls_id], density=True)
        ax.set_title(f"T2 · {col}", fontsize=9, fontweight="bold")
        ax.set_xlabel(col, fontsize=7)
        ax.set_ylabel("Density", fontsize=7)
        ax.tick_params(labelsize=7)
        ax.spines[["top", "right"]].set_visible(False)
        if i == 3:
            ax.legend(fontsize=7, loc="upper right")

    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig3_sensor_distributions.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved → {path}")
    return path


# ─────────────────────────────────────────────────────────────────────────────
# INFERENCE HELPERS (simulate IoT → Central DB → dual-track flow)
# ─────────────────────────────────────────────────────────────────────────────

class PredictiveMaintenance:
    """
    Represents the Central Database + dual-track inference layer.
    Input: a dict of sensor readings (as would arrive from the IoT layer).
    Output: structured results for Track 1 (Technician) and Track 2 (Owner).
    """

    def __init__(self, t1_pipe, t2_pipe):
        self.t1_pipe = t1_pipe
        self.t2_pipe = t2_pipe

    def predict_t1(self, sensor_dict: dict) -> dict:
        """Track 1 — Fault classification for technician."""
        X = np.array([[sensor_dict[f] for f in TRACK1_FEATURES]])
        cls_id   = int(self.t1_pipe.predict(X)[0])
        proba    = self.t1_pipe.predict_proba(X)[0] if hasattr(
                       self.t1_pipe.named_steps["clf"], "predict_proba") else None
        label    = TRACK1_LABELS[cls_id]
        is_anomaly = cls_id != 0
        return {
            "fault_class":  cls_id,
            "fault_label":  label,
            "is_anomaly":   is_anomaly,
            "confidence":   float(proba.max()) if proba is not None else None,
            "action":       "No action — vehicle operating normally."
                            if not is_anomaly
                            else f"⚠️  Anomaly detected: {label}. Escalate to LLM+RAG for fault brief."
        }

    def predict_t2(self, sensor_dict: dict) -> dict:
        """Track 2 — Risk detection for owner."""
        X = np.array([[sensor_dict[f] for f in TRACK2_FEATURES]])
        cls_id = int(self.t2_pipe.predict(X)[0])
        proba  = self.t2_pipe.predict_proba(X)[0] if hasattr(
                     self.t2_pipe.named_steps["clf"], "predict_proba") else None
        label  = TRACK2_LABELS[cls_id]
        emoji  = RISK_EMOJIS[cls_id]
        action = RISK_ACTIONS[cls_id]
        return {
            "risk_class":  cls_id,
            "risk_label":  label,
            "emoji":       emoji,
            "confidence":  float(proba.max()) if proba is not None else None,
            "push_alert":  None if cls_id == 0
                           else f"Escalate to LLM Summarizer (Bahasa Indonesia) → Push Alert",
            "action":      action
        }

    def predict_full(self, t1_sensors: dict, t2_sensors: dict) -> dict:
        """
        Full dual-track prediction matching the flow diagram.
        t1_sensors: 12 technician sensors (30-day rolling)
        t2_sensors: 12 owner sensors (12-hr daily window)
        """
        t1 = self.predict_t1(t1_sensors)
        t2 = self.predict_t2(t2_sensors)
        return {"track1_technician": t1, "track2_owner": t2}


def demo_inference(system: PredictiveMaintenance):
    """Run sample inferences representing the IoT → DB → dual-track flow."""
    print("\n" + "="*60)
    print("  DEMO — IoT Layer → Central Database → Dual-Track Inference")
    print("="*60)

    test_cases = [
        {
            "desc": "Healthy vehicle — all sensors nominal",
            "t1": dict(zip(TRACK1_FEATURES,
                           [0.45, 6.2, 14.0, 800, 10.5, 0, 90, 40, 35, 20, 14.2, 32])),
            "t2": dict(zip(TRACK2_FEATURES,
                           [0.45, 6.2, 14.0, 90, 40, 14.2, 32, 28, 55, 60, 10, 45])),
        },
        {
            "desc": "Battery degradation + Low TPMS",
            "t1": dict(zip(TRACK1_FEATURES,
                           [0.42, 6.5, 14.0, 800, 10.5, 0, 91, 39, 36, 20, 11.8, 33])),
            "t2": dict(zip(TRACK2_FEATURES,
                           [0.42, 6.5, 14.0, 91, 39, 11.8, 27.5, 29, 58, 55, 8, 50])),
        },
        {
            "desc": "Critical — overheating + low oil pressure",
            "t1": dict(zip(TRACK1_FEATURES,
                           [0.68, 4.5, 14.0, 810, 10.0, 6, 112, 17, 48, 42, 11.2, 57])),
            "t2": dict(zip(TRACK2_FEATURES,
                           [0.68, 4.5, 14.0, 112, 17, 11.2, 24, 38, 70, 8, 45, 95])),
        },
    ]

    for case in test_cases:
        print(f"\n  📡  Scenario: {case['desc']}")
        result = system.predict_full(case["t1"], case["t2"])

        t1 = result["track1_technician"]
        t2 = result["track2_owner"]

        print(f"  ┌─ Track 1 (Workshop/Mechanic)")
        print(f"  │  Fault Class : {t1['fault_class']} — {t1['fault_label']}")
        if t1["confidence"]:
            print(f"  │  Confidence  : {t1['confidence']:.1%}")
        print(f"  │  Action      : {t1['action']}")

        print(f"  └─ Track 2 (Vehicle Owner)")
        print(f"     Risk Class  : {t2['emoji']} {t2['risk_class']} — {t2['risk_label']}")
        if t2["confidence"]:
            print(f"     Confidence  : {t2['confidence']:.1%}")
        print(f"     Action      : {t2['action']}")
        if t2["push_alert"]:
            print(f"     Push Alert  : {t2['push_alert']}")


# ─────────────────────────────────────────────────────────────────────────────
# SAVE MODELS
# ─────────────────────────────────────────────────────────────────────────────

def save_models(t1_pipe, t2_pipe):
    t1_path = os.path.join(OUTPUT_DIR, "track1_fault_classifier.pkl")
    t2_path = os.path.join(OUTPUT_DIR, "track2_risk_classifier.pkl")
    joblib.dump(t1_pipe, t1_path)
    joblib.dump(t2_pipe, t2_path)
    print(f"\n  Model saved → {t1_path}")
    print(f"  Model saved → {t2_path}")
    return t1_path, t2_path


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "="*60)
    print("  VEHICLE PREDICTIVE MAINTENANCE — ML PIPELINE")
    print("="*60)

    # ── 1. Load data ──────────────────────────────────────────
    print("\n[1/5] Loading data...")
    df1, df2 = load_data()

    # ── 2. Train & evaluate both tracks ───────────────────────
    print("\n[2/5] Training Track 1 — Fault Classification (Technician)...")
    t1_out = run_track(
        "Track 1 — Workshop/Mechanic · Fault Classification",
        df1, TRACK1_FEATURES, TRACK1_TARGET, TRACK1_LABELS, TRACK1_COLOURS
    )

    print("\n[3/5] Training Track 2 — Risk Detection (Owner)...")
    t2_out = run_track(
        "Track 2 — Vehicle Owner · Risk Detection",
        df2, TRACK2_FEATURES, TRACK2_TARGET, TRACK2_LABELS, TRACK2_COLOURS
    )

    # ── 3. Generate figures ────────────────────────────────────
    print("\n[4/5] Generating visualisations...")
    p1 = fig_model_comparison(t1_out, t2_out)
    p2 = fig_confusion_and_importance(t1_out, t2_out)
    p3 = fig_sensor_distributions(df1, df2)

    # ── 4. Save models & run demo inference ───────────────────
    print("\n[5/5] Saving models & running inference demo...")
    save_models(t1_out["best_pipe"], t2_out["best_pipe"])

    system = PredictiveMaintenance(t1_out["best_pipe"], t2_out["best_pipe"])
    demo_inference(system)

    # ── 5. Summary ─────────────────────────────────────────────
    print("\n" + "="*60)
    print("  PIPELINE COMPLETE — SUMMARY")
    print("="*60)
    print(f"  Track 1 Best Model : {t1_out['best_name']}")
    print(f"    Test Accuracy    : {t1_out['results'][t1_out['best_name']]['acc']:.4f}")
    print(f"    CV F1 (Weighted) : {t1_out['results'][t1_out['best_name']]['cv_mean']:.4f}"
          f" ± {t1_out['results'][t1_out['best_name']]['cv_std']:.4f}")
    print(f"\n  Track 2 Best Model : {t2_out['best_name']}")
    print(f"    Test Accuracy    : {t2_out['results'][t2_out['best_name']]['acc']:.4f}")
    print(f"    CV F1 (Weighted) : {t2_out['results'][t2_out['best_name']]['cv_mean']:.4f}"
          f" ± {t2_out['results'][t2_out['best_name']]['cv_std']:.4f}")
    print(f"\n  Output files:")
    print(f"    fig1_model_comparison.png")
    print(f"    fig2_confusion_importance.png")
    print(f"    fig3_sensor_distributions.png")
    print(f"    track1_fault_classifier.pkl")
    print(f"    track2_risk_classifier.pkl")
    print("="*60)

    return system   # return for interactive use


if __name__ == "__main__":
    system = main()
