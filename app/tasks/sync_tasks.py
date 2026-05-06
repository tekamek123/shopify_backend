from app.tasks.celery_app import celery_app

@celery_app.task(name="sync_products_task")
def sync_products_task():
    """
    Placeholder for periodic product synchronization task.
    """
    return "Syncing products..."
