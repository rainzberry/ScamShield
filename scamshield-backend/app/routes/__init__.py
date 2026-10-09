def register_blueprints(app) -> None:
    from .analyze import bp as analyze_bp
    from .auth import bp as auth_bp
    from .dashboard import bp as dashboard_bp
    from .gmail import bp as gmail_bp
    from .reports import bp as reports_bp
    from .scans import bp as scans_bp
    from .settings import bp as settings_bp
    from .system import bp as system_bp

    for blueprint in (system_bp, auth_bp, analyze_bp, scans_bp, dashboard_bp,
                      reports_bp, gmail_bp, settings_bp):
        app.register_blueprint(blueprint)
