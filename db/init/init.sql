CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS points (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    geom GEOMETRY(Point, 4326)
);

INSERT INTO points (name, geom) VALUES
('Tour Eiffel', ST_GeomFromText('POINT(2.2945 48.8584)', 4326)),
('Arc de Triomphe', ST_GeomFromText('POINT(2.2950 48.8738)', 4326));
