
FEATURES = ["press_free", "freedom_index", "gdp", "absence_of_violence",
                        "electoral_integrity","civil_liberties",
                        "gov_stability", "human_rights"]
TARGET_BASE = 'system_index'
TARGET_NEXT_YEAR = 'system_next_year'

XGB_PARAMS = {
    'n_estimators': 200,
    'learning_rate': 0.05,
    'max_depth': 5,
    'random_state': 1,
    'objective': 'reg:squarederror'
}

CRISIS_THRESHOLD = -0.5
IMPROVEMENT_THRESHOLD = 0.5