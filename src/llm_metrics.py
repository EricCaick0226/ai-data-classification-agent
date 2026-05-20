_COUNTERS = {
    "match_profile_llm_calls": 0,
    "classifier_llm_calls": 0,
}


def reset_metrics():
    for key in _COUNTERS:
        _COUNTERS[key] = 0


def increment_metric(name):
    if name not in _COUNTERS:
        _COUNTERS[name] = 0

    _COUNTERS[name] += 1


def get_metrics():
    return dict(_COUNTERS)
