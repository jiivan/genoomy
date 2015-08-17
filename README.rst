========================
Genoomy
========================

Local Environment
-----------------

Start redis server

    redis-server

Start celery worker and monitoring (Flower)
    celery -A genoome worker -l debug
    celery -A genoome flower --broker=redis://localhost:6379/0

