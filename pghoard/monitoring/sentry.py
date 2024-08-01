import logging

LOG = logging.getLogger(__name__)


class SentryClient:
    def __init__(self, config):
        self.sentry = None
        if config is None:
            LOG.info("Sentry configuration not found, skipping setup")
            return
        dsn = config.get("dsn")
        if dsn is None:
            LOG.info("Sentry DSN not found, skipping setup")
            return
        try:
            import sentry_sdk
            from sentry_sdk.integrations.logging import LoggingIntegration
        except ImportError:
            LOG.info("Sentry SDK not found, skipping setup")
            return
        self.sentry = sentry_sdk
        sentry_logging = LoggingIntegration(
            level=logging.INFO,
            event_level=logging.CRITICAL,
        )
        tags = config.pop("tags", {})
        sentry_sdk.init(**config, integrations=[sentry_logging])
        for key, value in tags.items():
            sentry_sdk.set_tag(key, value)

    def gauge(self, metric, value, tags=None):
        pass

    def increase(self, metric, inc_value=1, tags=None):
        pass

    def unexpected_exception(self, ex, where, tags=None):
        if not self.sentry:
            return

        with self.sentry.push_scope() as scope:
            scope.set_tag("where", where)
            if tags and isinstance(tags, dict):
                for key, value in tags.items():
                    scope.set_tag(key, value)
            self.sentry.capture_exception(ex)
