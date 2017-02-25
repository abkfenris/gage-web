up:
	\rm -f web/celerybeat.pid
	\rm -f web/celerybeat-schedule
	docker-compose up -d --build
	docker-compose logs -f

down:
	docker-compose down

stop:
	docker-compose stop