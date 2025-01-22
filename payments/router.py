class PaymentsRouter:
    """
    A database router to manage operations for payments-related apps.
    """
    route_app_labels = {'payments'}

    def db_for_read(self, model, **hints):
        return None  # Use the default database for reads

    def db_for_write(self, model, **hints):
        return None  # Use the default database for writes

    def allow_relation(self, obj1, obj2, **hints):
        return True  # Allow relations in the default database

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure migrations for payments-related apps occur on the default database.
        """
        if db == 'default':  # Migrate to the default database
            if app_label in self.route_app_labels:
                return True
        return None
