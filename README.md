## Unrated App Whiskey Recommendations

Simple machine learning script that retrieves data from the database, and does collaborative filtering using FastAI in order to give users recommendations

## How to use

Get postgres
```cmd
docker pull postgres
```

Create postgres db
```cmd
docker run --name postgres_db -e POSTGRES_DB=ulu_prod -e POSTGRES_USER=ulu_backend -e POSTGRES_PASSWORD=%DB_PASSWORD% -p 5432:5432 -d postgres
```

1. Navigate too Dockerhub > Containers
2. Click on the three dots on the left of `postgres_db`
3. Click on `View Details`
4. Click on `Exec`
5. Paste in this command:
    ```bash
    psql -h localhost -p 5432 -U ulu_backend ulu_prod
    ```
6. Paste in this command:

    ```bash
    CREATE TABLE IF NOT EXISTS public.rating
    (
        id bigint NOT NULL,
        body character varying(255) COLLATE pg_catalog."default",
        created_at timestamp(6) with time zone,
        rating real NOT NULL,
        title character varying(255) COLLATE pg_catalog."default",
        user_id bigint,
        whiskey_id bigint,
        CONSTRAINT rating_pkey PRIMARY KEY (id),
        CONSTRAINT fkfre9fbbeav9d6cwh0us4senue FOREIGN KEY (user_id)
            REFERENCES public.user_data (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE NO ACTION
    );


    CREATE TABLE IF NOT EXISTS public.rating
    (
        id bigint NOT NULL,
        body character varying(255) COLLATE pg_catalog."default",
        created_at timestamp(6) with time zone,
        rating real NOT NULL,
        title character varying(255) COLLATE pg_catalog."default",
        user_id bigint,
        whiskey_id bigint,
        CONSTRAINT rating_pkey PRIMARY KEY (id),
        CONSTRAINT fkfre9fbbeav9d6cwh0us4senue FOREIGN KEY (user_id)
            REFERENCES public.user_data (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE NO ACTION
    );

    CREATE TABLE IF NOT EXISTS public.user_data
    (
        id bigint NOT NULL,
        created_at timestamp(6) with time zone,
        email character varying(255) COLLATE pg_catalog."default",
        img character varying(255) COLLATE pg_catalog."default",
        name character varying(255) COLLATE pg_catalog."default",
        password character varying(255) COLLATE pg_catalog."default",
        CONSTRAINT user_data_pkey PRIMARY KEY (id)
    );

    CREATE TABLE IF NOT EXISTS public.user_data_roles
    (
        user_data_id bigint NOT NULL,
        roles character varying(255) COLLATE pg_catalog."default",
        CONSTRAINT fk5fxok78n66h86q3t2ddr4wi8a FOREIGN KEY (user_data_id)
            REFERENCES public.user_data (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE NO ACTION
    );

    CREATE TABLE IF NOT EXISTS public.whiskey
    (
        id bigint NOT NULL,
        avg_score double precision,
        img character varying(255) COLLATE pg_catalog."default",
        percentage double precision NOT NULL,
        price double precision NOT NULL,
        summary character varying(255) COLLATE pg_catalog."default",
        title character varying(255) COLLATE pg_catalog."default",
        volume double precision NOT NULL,
        CONSTRAINT whiskey_pkey PRIMARY KEY (id)
    );
    ```

7. To ensure all relations, run the same command again.
8. Open up a terminal
9. Change Directory to this project
10. Run these commands:
```cmd
virtualenv .venv
```
```cmd
.venv\Scripts\activate
```
```cmd
pip install -r requirements.txt
```
10.1. If the `virtualenv .venv` command failed, do:
```cmd
pip install virtualenv
```
And then retry from step 8

11. Start the project using:
```cmd
python src\main.py
```
