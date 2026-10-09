import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.configs.settings import TEXT_MODEL_DIRNAME, URL_MODEL_DIRNAME  # noqa: E402
from ml.inference.engine import ScamShieldEngine  # noqa: E402
from ml.training.text_trainer import train_text_model  # noqa: E402
from ml.training.url_trainer import train_url_model  # noqa: E402
from .fixtures import TINY_TEXT_PARAMS, TINY_URL_PARAMS, make_frames  # noqa: E402


@pytest.fixture(scope="session")
def tiny_models_dir(tmp_path_factory):
    d = tmp_path_factory.mktemp("tiny_models")
    ttr, tva, utr, uva = make_frames()
    train_text_model(ttr, tva, d / TEXT_MODEL_DIRNAME, params=TINY_TEXT_PARAMS)
    train_url_model(utr, uva, d / URL_MODEL_DIRNAME, params=TINY_URL_PARAMS)
    return d


@pytest.fixture(scope="session")
def engine(tiny_models_dir):
    return ScamShieldEngine(models_dir=tiny_models_dir)


@pytest.fixture(scope="session")
def rules_engine(tmp_path_factory):
    """Engine with NO model artifacts -> rules-only mode."""
    return ScamShieldEngine(models_dir=tmp_path_factory.mktemp("no_models"))