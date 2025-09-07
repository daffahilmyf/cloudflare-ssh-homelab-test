from src.core.config import settings

def test_project_name_setting():
    assert settings.PROJECT_NAME == "Homelab API"
