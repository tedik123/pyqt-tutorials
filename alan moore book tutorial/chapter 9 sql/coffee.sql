
-- CREATE TABLE coffees (
-- --     primary key means it's unique
--   id INTEGER PRIMARY KEY,
--   coffee_brand TEXT NOT NULL,
--   coffee_name TEXT NOT NULL,
-- -- this is not saying both have to be unique but together they must be unique
-- -- so you can have same brand and different name
-- -- or same name different brand to reference different coffees
--   UNIQUE(coffee_brand, coffee_name)
-- );

CREATE TABLE roasts (
  id INTEGER PRIMARY KEY,
  description TEXT NOT NULL UNIQUE,
  color TEXT NOT NULL UNIQUE,
);

CREATE TABLE coffees (
--     primary key means it's unique
  id INTEGER PRIMARY KEY,
  coffee_brand TEXT NOT NULL,
  coffee_name TEXT NOT NULL,
-- this is not saying both have to be unique but together they must be unique
-- so you can have same brand and different name
-- or same name different brand to reference different coffees
  roast_id INTEGER REFERENCES roasts(id) -- here we are referencing another table as part of this table
  UNIQUE(coffee_brand, coffee_name)
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    coffee_id REFERENCES coffees(id),
    reviewer TEXT NOT NULL,
    review_date DATE NOT NULL DEFAULT CURRENT_DATE, --requiring it but setting a default value if not provided
    review TEXT NOT NULL,
);

-- we can insert new things like this
-- INSERT INTO table_name(column_name, column_name2,...) VALUES
        -- (value1, value2, ...),
        -- (value1, value2, ...
        -- )
INSERT INTO roasts(description, color)
    VALUES
    --description, color
    -- non-specified fields will default to whatever we said (usually NULL) unless we said NOT NULL
    ('Light', '#FFD99B'),
    ('Medium', '#947E5A'),
    ('Dark', '#473C2B'),
    ('Burnt to a Crisp', '#000000');

-- the INTEGER PRIMARY key has a default behavior of being incremented by 1 so it goes 1, 2, 3 ... n
-- like Light will be one and burnt to a crisp would be 4
-- since we know the values they should be we can now insert into the coffees table
-- IMPORTANT double quotes will be interpreted as the name of a database object so use single quotes for strings!!!
-- also with these references we can't insert into a reference that doesn't exist
-- but null is still an acceptable parameter for the reference!
INSERT INTO coffees(coffee_brand, coffee_name, roast_id)
    VALUES
        ('DUMPY''s Donuts', 'Breakfast Blend', 2), -- 2 is the medium roast
        ('Boise''s Better Than Average', 'Italian Roast', 3),
        ('Strawbunks', 'Sumatra', 3),
        ('Chartreuse Hillock', 'Pumpkin Spice', 1),
        ('Strawbunks', 'Espresso', 4),
        ('9 o''clock', 'Original Decaf', 2);

--to update rows you use the update function
-- where the id is 2 set it now to 4
-- also it always uses single = for equality and comparison
UPDATE coffees SET roast_id =4 WHERE id = 2;

-- on all strawbunks coffees we increment the roast id by one
UPDATE coffees SET roast_id = roast_id + 1
    WHERE coffee_brand LIKE 'StrawBunks';

-- selecting data
SELECT reviewer, review_date
--from defines from which data
FROM reviews
--where is the conditions that must be achieved
WHERE review_date > '2019-03-01'
-- and sort by DESCending
ORDER BY reviewer DESC;


--SELECT always returns one table even if it's only a single row
SELECT coffees.coffee_brand,
       coffees.coffee_name,
       roasts.description AS roast,
       COUNT(reviews.id) AS reviews,
FROM coffees
    --here we join the roasts with the coffees that have the same roast id
    JOIN roasts ON coffees.roast_id = roasts.id
    --then we add OUTER which means we add rows even without matching (just leave it blank i think :shrug:)
    LEFT OUTER JOIN reviews ON reviews.coffee_id = coffees.id
GROUP BY coffee_brand, coffee_name, roast_id
ORDER BY reviews DESC;

SELECT coffees.coffee_brand, coffees.coffee_name
FROM coffees
    JOIN (
    SELECT * FROM roasts WHERE id > (
	SELECT id FROM roasts WHERE description = 'Medium'
	    )) AS dark_roasts
    ON coffees.roast_id = dark_roasts.id
WHERE coffees.id IN (
    SELECT coffee_id FROM reviews WHERE reviewer = 'Maxwell');