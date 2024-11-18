class ListingRouter:
    """
    A database router to manage operations for abrmservices-related apps.
    """
    route_app_labels = {'abrmservices'}

    def db_for_read(self, model, **hints):
        """
        Direct read operations for abrmservices-related models to the 'default' database.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        """
        Direct write operations for abrmservices-related models to the 'default' database.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both models belong to abrmservices-related apps.
        """
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure migrations for abrmservices-related apps only occur on the 'default' database.
        """
        if app_label in self.route_app_labels:
            return db == 'default'
        return None
