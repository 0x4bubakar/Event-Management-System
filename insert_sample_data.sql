-- -----------------------------------------------------
-- Script for generating sample data 
-- (i.e. discounts, categories, venues, etc.) 
-- as required by assessment specification.
-- -----------------------------------------------------

-- Insert permanent discounts (early bird and student)
INSERT INTO discount(name, percent, event_id) VALUES
  ('Early Bird 20', 20, NULL),
  ('Early Bird 15', 15, NULL),
  ('Early Bird 10', 10, NULL),
  ('Early Bird 5', 5, NULL),
  ("Student 10", 10, NULL);

-- Insert sample event category names
INSERT INTO category(category_name) VALUES
  ('Exhibition'),
  ('Workshop'),
  ('Course'),
  ('Sports'),
  ('Theatre'),
  ('Musical'),
  ('Religious'),
  ('Birthday'),
  ('Conference'),
  ('Wedding');

-- Insert sample event venue information
INSERT INTO location(name, capacity, address) VALUES
  ('Ashton Gate Stadium', 150, 'Ashton Rd, Bristol BS3 2EJ'),
  ('Arnolfini', 100, 'Bush House, 16 Narrow Quay, House, Bristol BS1 4QA'),
  ('The Bristol Hippodrome', 120, 'St Augustine''s Parade, Bristol BS1 4UZ'),
  ('Bristol Old Vic', 110, 'King St, Bristol BS1 4ED'),
  ('Bristol Central Library', 50, 'College Green, Bristol BS1 5TL'),
  ('Royal West of England Academy', 100, 'Queens Rd, Clifton, Bristol BS8 1PX'),
  ('Creative Space A', 30, '39 High St, Staple Hill, Bristol BS16 5HD'),
  ('Creative Space B', 50, '40 High St, Staple Hill, Bristol BS16 5HD'),
  ('UWE Exhibition Centre', 300, 'University of the West of England Frenchay Campus, Coldharbour Ln, Bristol BS16 1QY'),
  ('Community Centre A', 60, 'Filton Community Centre, Elm Park, Filton, Bristol BS34 7PS');

-- Insert the category suitabilities for each location
INSERT INTO suitability(location_id, category_id) VALUES
  -- ashton gate stadium - suitable for musical, sports, and exhibition categories
  (1, 1), 
  (1, 4),
  (1, 6),
  -- arnolfini - suitable for exhibitions and workshops
  (2, 1),
  (2, 2),
  -- the hippodrome - suitable for theatre and musicals
  (3, 5),
  (3, 6),
  -- bristol old vic - suitable for theatre
  (4, 5),
  -- bristol central library - suitable for exhibitions
  (5, 1),
  -- royal west of england academy - suitable for exhibitions
  (6, 6),
  -- creative space a - suitable for workshops
  (7, 2),
  -- creative space b - suitable for workshops and courses
  (8, 2),
  (8, 3),
  -- uwe exhibition centre - suitable for weddings, workshops, conferences, and exhibitions
  (9, 10),
  (9, 2),
  (9, 9),
  (9, 1),
  -- community centre a - suitable for birthday parties or religious events
  (10, 8),
  (10, 7);