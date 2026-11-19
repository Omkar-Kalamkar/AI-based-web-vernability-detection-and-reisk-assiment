"""Optional scikit-learn classifier trained only on locally generated synthetic data.

The dataset is not real vulnerability data. It exists to demonstrate an ML pipeline
without claiming that a production model was trained. The transparent rule engine
remains authoritative for every score shown in the application.
"""

import random

from config import Config

FEATURE_ORDER = ["base_weight", "confidence", "exploitability", "endpoint_factor", "weakness_factor"]


class SyntheticRiskModel:
    def __init__(self):
        self.available = False
        self.model = None
        self.reason = "disabled"
        self.samples = 0

    def info(self):
        return {
            "enabled": Config.USE_SYNTHETIC_ML,
            "available": self.available,
            "algorithm": "RandomForestClassifier" if self.available else None,
            "training_data": "locally generated synthetic samples (not real-world vulnerability data)" if self.available else None,
            "samples": self.samples if self.available else 0,
            "note": (
                "Demonstration-only model. Scores are produced by the transparent weighted rule engine."
                if self.available
                else "ML component disabled; transparent rule-based scoring is active."
            ),
            "features": FEATURE_ORDER,
            "reason": self.reason,
        }

    def train(self):
        try:
            from sklearn.ensemble import RandomForestClassifier
        except ImportError:
            self.reason = "scikit-learn unavailable"
            return self
        random.seed(42)
        rows = []
        labels = []
        severities = ["informational", "low", "medium", "high", "critical"]
        weights = {"informational": 10, "low": 26, "medium": 52, "high": 76, "critical": 92}
        for _ in range(700):
            sev = random.choice(severities)
            base = weights[sev] + random.uniform(-6, 6)
            conf = random.choice([0.65, 0.85, 1.0])
            exp = random.choice([0.88, 1.0, 1.12])
            endpoint = 1 + random.choice([0.0, 0.12, 0.24, 0.36])
            weakness = 1 + random.choice([0.0, 0.04, 0.08, 0.12, 0.2])
            score = min(100.0, base * conf * exp * endpoint * weakness)
            label = "critical" if score >= 85 else "high" if score >= 70 else "medium" if score >= 45 else "low" if score >= 20 else "informational"
            rows.append([base, conf, exp, endpoint, weakness])
            labels.append(label)
        self.model = RandomForestClassifier(n_estimators=80, random_state=42, class_weight="balanced")
        self.model.fit(rows, labels)
        self.samples = len(rows)
        self.available = True
        self.reason = "trained on synthetic demonstration data"
        return self

    def predict(self, features):
        if not self.available or self.model is None:
            return None
        try:
            return str(self.model.predict([list(features)])[0])
        except Exception:
            return None


_model = None


def get_model():
    global _model
    if _model is None:
        _model = SyntheticRiskModel()
        if Config.USE_SYNTHETIC_ML:
            _model.train()
    return _model
