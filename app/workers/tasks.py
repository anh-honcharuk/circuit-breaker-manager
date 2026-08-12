from app.workers.celery_app import celery_app


@celery_app.task
def health_check_event(
    service_id: int,
    status: str,
) -> None:
    print(
        f"Health check event: "
        f"service_id={service_id}, status={status}"
    )