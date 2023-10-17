from admin_settings.models import ImportLog


class ImportLogHelper:
    @classmethod
    def info(cls, user, import_id, message):
        ImportLog.objects.create(user=user, import_id=import_id, level=ImportLog.Level.info, message=message)

    @classmethod
    def warning(cls, user, import_id, message):
        ImportLog.objects.create(user=user, import_id=import_id, level=ImportLog.Level.warning, message=message)

    @classmethod
    def error(cls, user, import_id, message):
        ImportLog.objects.create(user=user, import_id=import_id, level=ImportLog.Level.error, message=message)

    @classmethod
    def critical(cls, user, import_id, message):
        ImportLog.objects.create(user=user, import_id=import_id, level=ImportLog.Level.critical, message=message)
