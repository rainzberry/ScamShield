import pytest

from ml.configs.settings import MODELS_DIR, TEXT_MODEL_DIRNAME, URL_MODEL_DIRNAME
from ml.inference.model_store import load_bundle


@pytest.mark.skipif(not (MODELS_DIR / TEXT_MODEL_DIRNAME / "model.joblib").exists(), reason="real text model not trained yet")
def test_real_text_model_artifact():
    m = load_bundle(MODELS_DIR / TEXT_MODEL_DIRNAME)
    assert m.version.startswith("text-") and m.metadata["validation_metrics"]["n"] > 0


@pytest.mark.skipif(not (MODELS_DIR / URL_MODEL_DIRNAME / "model.joblib").exists(), reason="real URL model not trained yet")
def test_real_url_model_artifact():
    m = load_bundle(MODELS_DIR / URL_MODEL_DIRNAME)
    assert m.version.startswith("url-") and len(m.metadata["feature_names"]) == 36