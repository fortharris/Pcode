"""Shared helpers for stringly-typed and JSON-native settings values."""

# App-level settings stored as booleans in usedata.json.
APP_BOOL_KEYS = frozenset([
    "EnableAutoCompletion", "DynamicSearch", "MarkSearchOccurrence",
    "CallTips", "ShowWhiteSpaces", "ShowCaretLine", "ShowLineNumbers",
    "MatchBraces", "EnableFolding", "DocOnHover", "MarkOperationalLines",
    "ShowEdgeLine", "LineWrap", "EnableAlerts", "enableStyleGuide",
    "EnableAssistance", "SoundsEnabled", "ShowLineNumbers",
])

PROJECT_BOOL_KEYS = frozenset([
    "ClearOutputWindowOnRun", "RunWithArguments", "RunInternal",
    "UseVirtualEnv", "Closed", "ShowAllFiles", "LastCloseSuccessful",
])


def to_bool(value, default=False):
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in ("true", "1", "yes", "on")


def from_bool(value):
    return "True" if to_bool(value) else "False"


def normalize_app_settings(settings):
    for key in APP_BOOL_KEYS:
        if key in settings:
            settings[key] = to_bool(settings[key])
    return settings


def normalize_project_settings(settings):
    for key in PROJECT_BOOL_KEYS:
        if key in settings:
            settings[key] = to_bool(settings[key])
    return settings


def app_settings_for_json(settings):
    out = {}
    for key, value in settings.items():
        if key in APP_BOOL_KEYS:
            out[key] = to_bool(value)
        else:
            out[key] = value
    return out


def project_settings_for_json(settings):
    out = {}
    for key, value in settings.items():
        if key in PROJECT_BOOL_KEYS:
            out[key] = to_bool(value)
        else:
            out[key] = value
    return out
