# Blog API

## Run With Docker

- `docker-compose build api`
- `docker-compose run --rm api python ./app/manage.py makemigrations`
- `docker-compose run --rm api python ./app/manage.py migrate`
- `docker-compose run --rm api python ./app/manage.py collectstatic`
- `docker-compose run --rm api python ./app/manage.py createsuperuser`
- `docker-compose run --rm api python ./app/manage.py populatedb --total_user=10 --total_post=10`
- `docker-compose run --rm api python ./scripts/test.sh`
- `docker-compose run --rm api python ./app/manage.py shell -i ipython`
