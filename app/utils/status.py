from app.models import feature


def get_status(obj):
    if obj.status != feature.Feature.FAILED:
        return {"ok": True}
    else:
        return {"ok": False}
