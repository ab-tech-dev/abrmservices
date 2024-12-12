# class AuthRouter:
#     """
#     A database router to manage operations for auth-related apps.
#     """
#     route_app_labels = {'user', 'admin', 'contenttypes', 'sessions', 'auth'}

#     def db_for_read(self, model, **hints):
#         """
#         Direct read operations for auth-related models to the 'default' database.
#         """
#         if model._meta.app_label in self.route_app_labels:
#             return 'default'
#         return None

#     def db_for_write(self, model, **hints):
#         """
#         Direct write operations for auth-related models to the 'default' database.
#         """
#         if model._meta.app_label in self.route_app_labels:
#             return 'default'
#         return None

#     def allow_relation(self, obj1, obj2, **hints):
#         """
#         Allow relations if at least one model belongs to auth-related apps.
#         """
#         if (
#             obj1._meta.app_label in self.route_app_labels or
#             obj2._meta.app_label in self.route_app_labels
#         ):
#             return True
#         return None

#     def allow_migrate(self, db, app_label, model_name=None, **hints):
#         """
#         Ensure migrations for auth-related apps only occur on the 'default' database.
#         """
#         if app_label in self.route_app_labels:
#             return db == 'default'
#         return None


class AuthRouter:
    """
    A database router to manage operations for auth-related apps.
    """
    route_app_labels = {'auth', 'admin', 'contenttypes', 'sessions', 'user'}

    def db_for_read(self, model, **hints):
        """
        Point read operations for auth-related models to the 'users' database.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'users'
        return None

    def db_for_write(self, model, **hints):
        """
        Point write operations for auth-related models to the 'users' database.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'users'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if at least one model belongs to auth-related apps.
        """
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure migrations for auth-related apps only occur on the 'users' database.
        """
        if app_label in self.route_app_labels:
            return db == 'users'
        return None
