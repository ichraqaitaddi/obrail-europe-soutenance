-- ============================================================
-- ObRail Europe
-- Requêtes SQL d'extraction
-- Compétence C2 : Développer des requêtes SQL d'extraction
-- ============================================================


-- ============================================================
-- 1. Extraction des stations avec leur ville
-- ============================================================
-- Cette requête récupère les informations des stations
-- ainsi que la ville associée grâce à une jointure.
SELECT
    s.id,
    s.name AS station,
    s.latitude,
    s.longitude,
    c.name AS city
FROM stations s
JOIN cities c
    ON s.city_id = c.id;


-- ============================================================
-- 2. Extraction des routes avec leur opérateur
-- ============================================================
-- Cette requête permet d'obtenir les routes ferroviaires
-- ainsi que l'opérateur auquel elles sont associées.
SELECT
    r.id,
    r.short_name,
    r.long_name,
    o.name AS operator
FROM routes r
JOIN operators o
    ON r.operator_id = o.id;


-- ============================================================
-- 3. Extraction des trajets d'une route
-- ============================================================
-- Cette requête récupère les trajets appartenant
-- à une route donnée.
-- Ici, on utilise la route ayant l'identifiant 348.
SELECT
    t.id,
    t.gtfs_trip_id,
    t.headsign,
    t.service_id,
    t.direction_id
FROM trips t
WHERE t.route_id = 348;


-- ============================================================
-- 4. Nombre de trajets par route
-- ============================================================
-- Cette requête utilise une agrégation pour compter
-- le nombre de trajets associés à chaque route.
SELECT
    route_id,
    COUNT(*) AS nombre_trips
FROM trips
GROUP BY route_id
ORDER BY nombre_trips DESC;