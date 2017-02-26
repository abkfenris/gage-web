up:
	\rm -f web/celerybeat.pid
	\rm -f web/celerybeat-schedule
	docker-compose up -d --build
	docker-compose logs -f

down:
	docker-compose down

stop:
	docker-compose stop

test:
	docker-compose --project-name testing -f docker-compose.test.yml up -d --build
	docker-compose --project-name testing -f docker-compose.test.yml run wait
	docker-compose --project-name testing -f docker-compose.test.yml run web py.test -v tests
	docker-compose --project-name testing -f docker-compose.test.yml down