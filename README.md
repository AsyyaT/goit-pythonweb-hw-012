## Project set up

add .env file based on .env.example

run:

 > docker-compose up --build

If for some reason migrations weren't applied please run this command

 > docker-compose exec app alembic upgrade head
 
To be able to login is necessary to confirm email.
