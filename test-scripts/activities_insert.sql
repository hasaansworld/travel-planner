-- Check-in history for user 125003 (coffee enthusiast and art lover)
-- This user has consistent preferences: specialty coffee, art galleries/museums, and casual dining

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Coffee shops - main interest, visits regularly
(125003, 40.7580, -73.9855, 'Blue Bottle Coffee', 'coffee_shop', '456 5th Ave, New York, NY 10016', '2024-12-15 08:30:00'),
(125003, 40.7505, -73.9934, 'Stumptown Coffee Roasters', 'coffee_shop', '18 W 29th St, New York, NY 10001', '2024-12-13 09:15:00'),
(125003, 40.7282, -74.0776, 'Joe Coffee', 'coffee_shop', '141 Waverly Pl, New York, NY 10014', '2024-12-11 08:45:00'),
(125003, 40.7505, -73.9934, 'Intelligentsia Coffee', 'coffee_shop', '180 10th Ave, New York, NY 10011', '2024-12-09 07:30:00'),
(125003, 40.7829, -73.9654, 'Irving Farm Coffee Roasters', 'coffee_shop', '79 E 79th St, New York, NY 10075', '2024-12-07 08:00:00'),
(125003, 40.7282, -74.0776, 'La Colombe Coffee Roasters', 'coffee_shop', '270 Lafayette St, New York, NY 10012', '2024-12-05 09:30:00'),
(125003, 40.7505, -73.9934, 'Toby\'s Estate Coffee', 'coffee_shop', '125 N 6th St, Brooklyn, NY 11249', '2024-12-03 08:15:00'),
(125003, 40.7580, -73.9855, 'Think Coffee', 'coffee_shop', '248 Mercer St, New York, NY 10012', '2024-12-01 09:00:00'),

-- Art galleries and museums - secondary passion
(125003, 40.7794, -73.9632, 'Metropolitan Museum of Art', 'museum', '1000 5th Ave, New York, NY 10028', '2024-12-14 14:20:00'),
(125003, 40.7614, -73.9776, 'Museum of Modern Art', 'museum', '11 W 53rd St, New York, NY 10019', '2024-12-12 15:30:00'),
(125003, 40.7282, -74.0776, 'Whitney Museum of American Art', 'museum', '99 Gansevoort St, New York, NY 10014', '2024-12-10 13:45:00'),
(125003, 40.7505, -73.9934, 'David Zwirner Gallery', 'art_gallery', '525 W 19th St, New York, NY 10011', '2024-12-08 16:15:00'),
(125003, 40.7829, -73.9654, 'Gagosian Gallery', 'art_gallery', '980 Madison Ave, New York, NY 10075', '2024-12-06 14:00:00'),
(125003, 40.7282, -74.0776, 'New Museum', 'museum', '235 Bowery, New York, NY 10002', '2024-12-04 12:30:00'),
(125003, 40.7505, -73.9934, 'Hauser & Wirth Gallery', 'art_gallery', '542 W 22nd St, New York, NY 10011', '2024-12-02 15:45:00'),

-- Casual dining - prefers simple, quality food
(125003, 40.7505, -73.9934, 'Joe\'s Pizza', 'pizza_restaurant', '7 Carmine St, New York, NY 10014', '2024-12-13 12:30:00'),
(125003, 40.7282, -74.0776, 'Katz\'s Delicatessen', 'deli', '205 E Houston St, New York, NY 10002', '2024-12-11 13:15:00'),
(125003, 40.7580, -73.9855, 'The Halal Guys', 'fast_food_restaurant', '307 E 53rd St, New York, NY 10022', '2024-12-09 12:45:00'),
(125003, 40.7829, -73.9654, 'Levain Bakery', 'bakery', '1484 3rd Ave, New York, NY 10028', '2024-12-07 14:30:00'),
(125003, 40.7505, -73.9934, 'Xi\'an Famous Foods', 'chinese_restaurant', '248 E 14th St, New York, NY 10003', '2024-12-05 18:20:00'),
(125003, 40.7282, -74.0776, 'Prince Street Pizza', 'pizza_restaurant', '27 Prince St, New York, NY 10012', '2024-12-03 19:00:00'),

-- Bookstores - enjoys browsing
(125003, 40.7282, -74.0776, 'The Strand Book Store', 'book_store', '828 Broadway, New York, NY 10003', '2024-12-12 16:45:00'),
(125003, 40.7505, -73.9934, 'Housing Works Bookstore Cafe', 'book_store', '126 Crosby St, New York, NY 10012', '2024-12-08 17:30:00'),
(125003, 40.7829, -73.9654, 'Book Culture', 'book_store', '2915 Broadway, New York, NY 10025', '2024-12-04 11:15:00'),

-- Parks - for quiet moments and walking
(125003, 40.7829, -73.9654, 'Central Park', 'park', 'Central Park, New York, NY 10024', '2024-12-10 16:00:00'),
(125003, 40.7282, -74.0776, 'Washington Square Park', 'park', 'Washington Square, New York, NY 10012', '2024-12-06 17:15:00'),
(125003, 40.7505, -73.9934, 'High Line', 'park', 'High Line, New York, NY 10011', '2024-12-02 10:30:00'),

-- Essential services
(125003, 40.7282, -74.0776, 'Whole Foods Market', 'grocery_store', '270 Greenwich St, New York, NY 10007', '2024-12-08 18:45:00'),
(125003, 40.7505, -73.9934, 'Duane Reade', 'pharmacy', '378 6th Ave, New York, NY 10014', '2024-12-04 19:30:00');

-- Check-in history for user 125004 (fitness enthusiast and tech professional)
-- This user focuses on morning workouts, healthy eating, and a tech job in Chelsea.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Gyms and fitness centers - main interest, frequent morning visits
(125004, 40.7404, -74.0016, 'Equinox High Line', 'gym', '60 10th Ave, New York, NY 10014', '2024-12-16 06:30:00'),
(125004, 40.7359, -73.9911, 'Barry''s Chelsea', 'fitness_center', '135 W 20th St, New York, NY 10011', '2024-12-14 07:00:00'),
(125004, 40.7420, -74.0048, 'SoulCycle West Village', 'fitness_center', '126 Leroy St, New York, NY 10014', '2024-12-12 06:45:00'),
(125004, 40.7404, -74.0016, 'Equinox High Line', 'gym', '60 10th Ave, New York, NY 10014', '2024-12-11 07:15:00'),
(125004, 40.7359, -73.9911, 'Barry''s Chelsea', 'fitness_center', '135 W 20th St, New York, NY 10011', '2024-12-09 06:30:00'),
(125004, 40.7404, -74.0016, 'Equinox High Line', 'gym', '60 10th Ave, New York, NY 10014', '2024-12-07 08:00:00'),
(125004, 40.7420, -74.0048, 'SoulCycle West Village', 'fitness_center', '126 Leroy St, New York, NY 10014', '2024-12-05 07:00:00'),
(125004, 40.7404, -74.0016, 'Equinox High Line', 'gym', '60 10th Ave, New York, NY 10014', '2024-12-04 06:45:00'),

-- Healthy dining - frequent lunch and post-workout spots
(125004, 40.7441, -74.0062, 'Sweetgreen', 'vegetarian_restaurant', '600 11th Ave, New York, NY 10036', '2024-12-16 12:30:00'),
(125004, 40.7391, -73.9959, 'Juice Generation', 'juice_shop', '210 8th Ave, New York, NY 10011', '2024-12-14 08:15:00'),
(125004, 40.7400, -74.0050, 'Whole Foods Market', 'grocery_store', '250 7th Ave, New York, NY 10001', '2024-12-12 18:30:00'),
(125004, 40.7441, -74.0062, 'DIG', 'restaurant', '459 W 15th St, New York, NY 10011', '2024-12-11 13:00:00'),
(125004, 40.7391, -73.9959, 'Juice Generation', 'juice_shop', '210 8th Ave, New York, NY 10011', '2024-12-09 07:45:00'),
(125004, 40.7441, -74.0062, 'Sweetgreen', 'vegetarian_restaurant', '600 11th Ave, New York, NY 10036', '2024-12-05 12:45:00'),

-- Work and errands
(125004, 40.7411, -74.0048, 'Google', 'corporate_office', '111 8th Ave, New York, NY 10011', '2024-12-16 09:00:00'),
(125004, 40.7411, -74.0048, 'Google', 'corporate_office', '111 8th Ave, New York, NY 10011', '2024-12-11 09:15:00'),
(125004, 40.7411, -74.0048, 'Google', 'corporate_office', '111 8th Ave, New York, NY 10011', '2024-12-09 08:55:00'),
(125004, 40.7411, -74.0048, 'Google', 'corporate_office', '111 8th Ave, New York, NY 10011', '2024-12-05 09:05:00'),
(125004, 40.7423, -74.0035, 'Nike NYC', 'sporting_goods_store', '855 6th Ave, New York, NY 10001', '2024-12-14 14:00:00'),
(125004, 40.7400, -74.0050, 'CVS', 'pharmacy', '272 8th Ave, New York, NY 10011', '2024-12-07 18:00:00'),

-- Recreation
(125004, 40.7711, -73.9742, 'Central Park Running Path', 'park', 'Central Park, New York, NY', '2024-12-15 10:00:00'),
(125004, 40.7450, -74.0084, 'The High Line', 'park', 'High Line, New York, NY', '2024-12-08 15:30:00'),
(125004, 40.7711, -73.9742, 'Prospect Park', 'park', 'Prospect Park, Brooklyn, NY', '2024-12-01 11:00:00');

-- Check-in history for user 125005 (university student with a social life)
-- This user's life revolves around the NYU campus, libraries, cheap eats, and nightlife.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- University and study spots - core daily activities
(125005, 40.7295, -73.9965, 'NYU Bobst Library', 'library', '70 Washington Square S, New York, NY 10012', '2024-12-16 10:00:00'),
(125005, 40.7308, -73.9973, 'NYU Stern School of Business', 'university', '44 W 4th St, New York, NY 10012', '2024-12-16 14:00:00'),
(125005, 40.7295, -73.9965, 'NYU Bobst Library', 'library', '70 Washington Square S, New York, NY 10012', '2024-12-13 11:30:00'),
(125005, 40.7291, -73.9954, 'NYU Silver Center', 'university', '100 Washington Square E, New York, NY 10003', '2024-12-13 15:00:00'),
(125005, 40.7295, -73.9965, 'NYU Bobst Library', 'library', '70 Washington Square S, New York, NY 10012', '2024-12-11 13:00:00'),
(125005, 40.7308, -73.9973, 'NYU Stern School of Business', 'university', '44 W 4th St, New York, NY 10012', '2024-12-11 16:00:00'),
(125005, 40.7330, -73.9942, 'The Strand Book Store', 'book_store', '828 Broadway, New York, NY 10003', '2024-12-09 17:00:00'),
(125005, 40.7295, -73.9965, 'NYU Bobst Library', 'library', '70 Washington Square S, New York, NY 10012', '2024-12-08 14:00:00'),

-- Nightlife and bars - frequent weekend and evening activity
(125005, 40.7262, -73.9959, 'The Up & Up', 'bar', '116 MacDougal St, New York, NY 10012', '2024-12-14 22:30:00'),
(125005, 40.7219, -73.9885, 'Pianos', 'bar', '158 Ludlow St, New York, NY 10002', '2024-12-13 23:00:00'),
(125005, 40.7482, -74.0020, 'Marquee New York', 'night_club', '289 10th Ave, New York, NY 10001', '2024-12-07 23:59:00'),
(125005, 40.7265, -73.9937, 'McSorley''s Old Ale House', 'bar', '15 E 7th St, New York, NY 10003', '2024-12-06 21:00:00'),
(125005, 40.7251, -73.9926, 'The Dead Rabbit', 'bar', '30 Water St, New York, NY 10004', '2024-12-02 22:00:00'),

-- Food and Coffee - casual and affordable
(125005, 40.7303, -73.9996, 'Joe''s Pizza', 'pizza_restaurant', '7 Carmine St, New York, NY 10014', '2024-12-16 12:45:00'),
(125005, 40.7300, -73.9937, 'Think Coffee', 'coffee_shop', '1 Bleecker St, New York, NY 10012', '2024-12-13 09:00:00'),
(125005, 40.7288, -73.9961, 'Mamoun''s Falafel', 'middle_eastern_restaurant', '119 MacDougal St, New York, NY 10012', '2024-12-11 18:30:00'),
(125005, 40.7313, -73.9901, 'Veselka', 'restaurant', '144 2nd Ave, New York, NY 10003', '2024-12-08 20:00:00'),
(125005, 40.7303, -73.9996, 'Joe''s Pizza', 'pizza_restaurant', '7 Carmine St, New York, NY 10014', '2024-12-06 19:30:00'),
(125005, 40.7300, -73.9937, 'Think Coffee', 'coffee_shop', '1 Bleecker St, New York, NY 10012', '2024-12-04 10:15:00'),

-- Essentials and transit
(125005, 40.7309, -73.9976, 'W 4 St-Wash Sq', 'subway_station', '371 6th Ave, New York, NY 10014', '2024-12-16 09:45:00'),
(125005, 40.7305, -73.9927, 'Trader Joe''s', 'grocery_store', '142 E 14th St, New York, NY 10003', '2024-12-10 19:00:00'),
(125005, 40.7299, -73.9988, 'University Place Laundromat', 'laundry', '11 University Pl, New York, NY 10003', '2024-12-08 11:00:00'),
(125005, 40.7309, -73.9976, 'W 4 St-Wash Sq', 'subway_station', '371 6th Ave, New York, NY 10014', '2024-12-06 20:45:00');

-- Check-in history for user 125006 (parent with young children)
-- This user's activities are centered around family-friendly locations in the Upper West Side.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Child-focused activities - main priority
(125006, 40.7813, -73.9737, 'American Museum of Natural History', 'museum', '200 Central Park West, New York, NY 10024', '2024-12-14 11:00:00'),
(125006, 40.7851, -73.9680, 'Ancient Playground', 'playground', 'East Side of Central Park, New York, NY 10028', '2024-12-15 15:00:00'),
(125006, 40.7900, -73.9700, 'Children''s Museum of Manhattan', 'museum', '212 W 83rd St, New York, NY 10024', '2024-12-08 10:30:00'),
(125006, 40.7678, -73.9718, 'Central Park Zoo', 'zoo', 'East 64th Street, New York, NY 10021', '2024-12-07 13:00:00'),
(125006, 40.7813, -73.9737, 'Heckscher Playground', 'playground', 'Central Park South, New York, NY 10019', '2024-12-01 16:00:00'),
(125006, 40.7950, -73.9640, 'Bank Street School for Children', 'primary_school', '610 W 112th St, New York, NY 10025', '2024-12-16 08:30:00'),
(125006, 40.7950, -73.9640, 'Bank Street School for Children', 'primary_school', '610 W 112th St, New York, NY 10025', '2024-12-13 15:30:00'),
(125006, 40.7950, -73.9640, 'Bank Street School for Children', 'primary_school', '610 W 112th St, New York, NY 10025', '2024-12-11 08:35:00'),

-- Dining - family-friendly restaurants
(125006, 40.7840, -73.9790, 'Shake Shack', 'hamburger_restaurant', '366 Columbus Ave, New York, NY 10024', '2024-12-14 13:30:00'),
(125006, 40.7865, -73.9768, 'Carmine''s', 'italian_restaurant', '2450 Broadway, New York, NY 10024', '2024-12-10 18:00:00'),
(125006, 40.7828, -73.9789, 'Levain Bakery', 'bakery', '351 Amsterdam Ave, New York, NY 10024', '2024-12-08 12:00:00'),
(125006, 40.7833, -73.9805, 'Flor de Mayo', 'restaurant', '484 Amsterdam Ave, New York, NY 10024', '2024-12-05 19:00:00'),
(125006, 40.7840, -73.9790, 'Shake Shack', 'hamburger_restaurant', '366 Columbus Ave, New York, NY 10024', '2024-12-01 12:30:00'),

-- Shopping and Errands
(125006, 40.7950, -73.9720, 'Whole Foods Market', 'grocery_store', '808 Columbus Ave, New York, NY 10025', '2024-12-15 10:00:00'),
(125006, 40.7860, -73.9798, 'Book Culture on Columbus', 'book_store', '450 Columbus Ave, New York, NY 10024', '2024-12-12 16:30:00'),
(125006, 40.7877, -73.9775, 'Zabar''s', 'grocery_store', '2245 Broadway, New York, NY 10024', '2024-12-10 11:00:00'),
(125006, 40.7950, -73.9720, 'Whole Foods Market', 'grocery_store', '808 Columbus Ave, New York, NY 10025', '2024-12-09 17:30:00'),
(125006, 40.7890, -73.9750, 'Duane Reade', 'pharmacy', '2330 Broadway, New York, NY 10024', '2024-12-06 09:30:00'),
(125006, 40.7810, -73.9810, 'Lowe''s Home Improvement', 'home_improvement_store', '2008 Broadway, New York, NY 10023', '2024-12-04 14:00:00'),
(125006, 40.7850, -73.9800, 'Petco', 'pet_store', '2220 Broadway, New York, NY 10024', '2024-12-02 18:45:00');

-- Check-in history for user 125007 (business traveler)
-- This user's activities reflect a short, intensive business trip focused on Midtown Manhattan.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Travel and Accommodation
(125007, 40.6413, -73.7781, 'John F. Kennedy International Airport', 'airport', 'Queens, NY 11430', '2024-12-09 15:30:00'),
(125007, 40.7577, -73.9857, 'New York Marriott Marquis', 'hotel', '1535 Broadway, New York, NY 10036', '2024-12-09 17:00:00'),
(125007, 40.7577, -73.9857, 'New York Marriott Marquis', 'hotel', '1535 Broadway, New York, NY 10036', '2024-12-12 09:00:00'),
(125007, 40.6413, -73.7781, 'John F. Kennedy International Airport', 'airport', 'Queens, NY 11430', '2024-12-12 11:00:00'),

-- Business Meetings and Work
(125007, 40.7562, -73.9868, 'Morgan Stanley', 'corporate_office', '1585 Broadway, New York, NY 10036', '2024-12-10 09:30:00'),
(125007, 40.7615, -73.9776, 'Javits Center', 'convention_center', '429 11th Ave, New York, NY 10001', '2024-12-10 14:00:00'),
(125007, 40.7527, -73.9791, 'Bank of America Tower', 'corporate_office', '1 Bryant Park, New York, NY 10036', '2024-12-11 10:00:00'),
(125007, 40.7550, -73.9860, 'WeWork Times Square', 'corporate_office', '1460 Broadway, New York, NY 10036', '2024-12-11 15:30:00'),
(125007, 40.7577, -73.9857, 'Hotel Lobby Bar', 'bar', '1535 Broadway, New York, NY 10036', '2024-12-11 17:00:00'),

-- Dining (client dinners and quick meals)
(125007, 40.7583, -73.9862, 'The Capital Grille', 'steak_house', '120 W 51st St, New York, NY 10020', '2024-12-09 20:00:00'),
(125007, 40.7590, -73.9845, 'Pret A Manger', 'sandwich_shop', '630 7th Ave, New York, NY 10036', '2024-12-10 12:30:00'),
(125007, 40.7514, -73.9843, 'Keens Steakhouse', 'steak_house', '72 W 36th St, New York, NY 10018', '2024-12-10 19:30:00'),
(125007, 40.7590, -73.9845, 'Starbucks', 'coffee_shop', '1540 Broadway, New York, NY 10036', '2024-12-11 08:30:00'),
(125007, 40.7614, -73.9822, 'Le Bernardin', 'fine_dining_restaurant', '155 W 51st St, New York, NY 10019', '2024-12-11 20:30:00'),

-- Essentials and Transit
(125007, 40.7559, -73.9869, 'Times Sq-42 St Station', 'subway_station', 'Broadway & 42nd St, New York, NY 10036', '2024-12-10 09:15:00'),
(125007, 40.7565, -73.9880, 'Penn Station', 'train_station', '8th Ave & 31st St, New York, NY 10001', '2024-12-10 18:00:00'),
(125007, 40.7577, -73.9857, 'Hotel Gym', 'gym', '1535 Broadway, New York, NY 10036', '2024-12-11 06:30:00'),
(125007, 40.7570, -73.9860, 'Duane Reade', 'pharmacy', '1550 Broadway, New York, NY 10036', '2024-12-11 22:00:00'),
(125007, 40.7575, -73.9901, 'JFK AirTrain', 'light_rail_station', 'Jamaica Station, Queens, NY 11435', '2024-12-12 10:00:00'),
(125007, 40.7562, -73.9868, 'Midtown Comics', 'book_store', '200 W 40th St, New York, NY 10018', '2024-12-10 13:15:00');

-- Check-in history for user 125008 (history buff and researcher)
-- This user frequents museums, libraries, historical sites, and quiet cafes for study.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Museums and Historical Sites - primary interest
(125008, 40.7794, -73.9632, 'Metropolitan Museum of Art', 'museum', '1000 5th Ave, New York, NY 10028', '2024-12-16 11:00:00'),
(125008, 40.7143, -74.0131, '9/11 Memorial & Museum', 'museum', '180 Greenwich St, New York, NY 10007', '2024-12-14 14:00:00'),
(125008, 40.7061, -73.9934, 'Tenement Museum', 'museum', '97 Orchard St, New York, NY 10002', '2024-12-13 12:30:00'),
(125008, 40.7813, -73.9737, 'American Museum of Natural History', 'museum', '200 Central Park West, New York, NY 10024', '2024-12-11 10:30:00'),
(125008, 40.7042, -74.0115, 'Fraunces Tavern Museum', 'historical_place', '54 Pearl St, New York, NY 10004', '2024-12-09 15:00:00'),
(125008, 40.7075, -74.0111, 'Federal Hall', 'historical_landmark', '26 Wall St, New York, NY 10005', '2024-12-07 13:00:00'),
(125008, 40.7127, -74.0042, 'African Burial Ground National Monument', 'monument', '290 Broadway, New York, NY 10007', '2024-12-05 16:00:00'),
(125008, 40.8296, -73.9262, 'The Cloisters', 'museum', '99 Margaret Corbin Dr, New York, NY 10040', '2024-12-03 12:00:00'),

-- Libraries and Research
(125008, 40.7532, -73.9822, 'NY Public Library - Stephen A. Schwarzman Building', 'library', '476 5th Ave, New York, NY 10018', '2024-12-17 10:00:00'),
(125008, 40.7638, -73.9859, 'New York Historical Society', 'library', '170 Central Park West, New York, NY 10024', '2024-12-12 13:00:00'),
(125008, 40.7532, -73.9822, 'NY Public Library - Stephen A. Schwarzman Building', 'library', '476 5th Ave, New York, NY 10018', '2024-12-10 09:30:00'),
(125008, 40.7295, -73.9965, 'NYU Bobst Library', 'library', '70 Washington Square S, New York, NY 10012', '2024-12-06 14:00:00'),

-- Cafes and Dining
(125008, 40.7525, -73.9829, 'Culture Espresso', 'coffee_shop', '72 W 38th St, New York, NY 10018', '2024-12-17 13:00:00'),
(125008, 40.7766, -73.9638, 'Bluestone Lane', 'cafe', '1085 5th Ave, New York, NY 10128', '2024-12-16 14:00:00'),
(125008, 40.7042, -74.0115, 'Fraunces Tavern', 'bar_and_grill', '54 Pearl St, New York, NY 10004', '2024-12-09 17:30:00'),
(125008, 40.7061, -73.9934, 'Katz''s Delicatessen', 'deli', '205 E Houston St, New York, NY 10002', '2024-12-04 19:00:00'),
(125008, 40.7532, -73.9822, 'Bryant Park Cafe', 'cafe', 'Bryant Park, New York, NY 10018', '2024-12-02 12:45:00'),

-- Recreation and Miscellaneous
(125008, 40.7527, -73.9836, 'Bryant Park', 'park', 'New York, NY 10018', '2024-12-10 12:15:00'),
(125008, 40.7330, -73.9942, 'The Strand Book Store', 'book_store', '828 Broadway, New York, NY 10003', '2024-12-08 16:00:00'),
(125008, 40.7075, -74.0094, 'Trinity Church', 'church', '89 Broadway, New York, NY 10006', '2024-12-07 15:00:00'),
(125008, 40.7118, -74.0002, 'Brooklyn Bridge', 'tourist_attraction', 'Brooklyn Bridge, New York, NY 10038', '2024-12-01 17:00:00');

-- Check-in history for user 125009 (indie musician and live music fan)
-- This user's life is about rehearsals, gigs, instrument shops, and the Brooklyn/LES music scene.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Music Venues and Performance - core interest
(125009, 40.7198, -73.9602, 'Brooklyn Bowl', 'bowling_alley', '61 Wythe Ave, Brooklyn, NY 11249', '2024-12-14 21:00:00'),
(125009, 40.7221, -73.9873, 'The Bowery Ballroom', 'concert_hall', '6 Delancey St, New York, NY 10002', '2024-12-12 20:30:00'),
(125009, 40.7219, -73.9885, 'Pianos', 'bar', '158 Ludlow St, New York, NY 10002', '2024-12-10 22:00:00'),
(125009, 40.7145, -73.9565, 'Music Hall of Williamsburg', 'concert_hall', '66 N 6th St, Brooklyn, NY 11211', '2024-12-07 20:00:00'),
(125009, 40.7259, -73.9975, 'Blue Note Jazz Club', 'night_club', '131 W 3rd St, New York, NY 10012', '2024-12-05 23:00:00'),
(125009, 40.7203, -73.9899, 'Rockwood Music Hall', 'concert_hall', '196 Allen St, New York, NY 10002', '2024-12-02 21:30:00'),
(125009, 40.6833, -73.9760, 'Barclays Center', 'arena', '620 Atlantic Ave, Brooklyn, NY 11217', '2024-11-30 19:30:00'),

-- Rehearsal and Gear
(125009, 40.7180, -73.9577, 'Main Drag Music', 'store', '50 S 1st St, Brooklyn, NY 11249', '2024-12-15 14:00:00'),
(125009, 40.7195, -73.9869, 'Rivington Guitars', 'store', '73 E 4th St, New York, NY 10003', '2024-12-13 16:00:00'),
(125009, 40.7151, -73.9453, 'Pirate Studios', 'art_studio', '153 Morgan Ave, Brooklyn, NY 11237', '2024-12-11 18:00:00'),
(125009, 40.7151, -73.9453, 'Pirate Studios', 'art_studio', '153 Morgan Ave, Brooklyn, NY 11237', '2024-12-09 19:30:00'),
(125009, 40.7481, -73.9906, 'Sam Ash Music Stores', 'electronics_store', '333 W 34th St, New York, NY 10001', '2024-12-04 15:00:00'),

-- Food and Drink (late night, casual)
(125009, 40.7213, -73.9568, 'Peter Luger Steak House', 'steak_house', '178 Broadway, Brooklyn, NY 11211', '2024-12-15 22:00:00'),
(125009, 40.7225, -73.9570, 'Diner', 'diner', '85 Broadway, Brooklyn, NY 11249', '2024-12-13 01:00:00'),
(125009, 40.7145, -73.9612, 'Devoción', 'coffee_shop', '69 Grand St, Brooklyn, NY 11249', '2024-12-11 11:00:00'),
(125009, 40.7180, -73.9950, 'Scarr''s Pizza', 'pizza_restaurant', '22 Orchard St, New York, NY 10002', '2024-12-07 23:00:00'),
(125009, 40.7145, -73.9612, 'Variety Coffee Roasters', 'coffee_shop', '142 Graham Ave, Brooklyn, NY 11206', '2024-12-04 12:00:00'),
(125009, 40.7049, -73.9333, 'Roberta''s Pizza', 'pizza_restaurant', '261 Moore St, Brooklyn, NY 11206', '2024-12-01 20:30:00'),

-- Transit and Essentials
(125009, 40.7101, -73.9634, 'Bedford Ave Station', 'subway_station', 'Bedford Ave & N 7th St, Brooklyn, NY 11211', '2024-12-12 19:45:00'),
(125009, 40.7130, -73.9590, 'Foodtown', 'grocery_store', '125 N 6th St, Brooklyn, NY 11249', '2024-12-09 17:00:00'),
(125009, 40.7101, -73.9634, 'Bedford Ave Station', 'subway_station', 'Bedford Ave & N 7th St, Brooklyn, NY 11211', '2024-12-07 19:30:00'),
(125009, 40.7210, -73.9870, 'Whole Foods Market', 'grocery_store', '95 E Houston St, New York, NY 10002', '2024-12-03 18:00:00');

-- Check-in history for user 125010 (fashion enthusiast and shopper)
-- This user's activities are concentrated in SoHo and the West Village, focusing on high-end retail, brunch, and beauty.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Shopping - primary activity, mostly on weekends
(125010, 40.7251, -74.0022, 'Prada Broadway', 'clothing_store', '575 Broadway, New York, NY 10012', '2024-12-15 14:30:00'),
(125010, 40.7248, -74.0000, 'Bloomingdale''s', 'department_store', '504 Broadway, New York, NY 10012', '2024-12-15 15:45:00'),
(125010, 40.7225, -73.9983, 'Kith', 'shoe_store', '337 Lafayette St, New York, NY 10012', '2024-12-14 13:00:00'),
(125010, 40.7200, -73.9960, 'Reformation', 'clothing_store', '23 Howard St, New York, NY 10013', '2024-12-14 14:15:00'),
(125010, 40.7275, -74.0010, 'A.P.C.', 'clothing_store', '131 Mercer St, New York, NY 10012', '2024-12-08 16:00:00'),
(125010, 40.7325, -74.0030, 'Diptyque', 'home_goods_store', '377 Bleecker St, New York, NY 10014', '2024-12-07 17:30:00'),
(125010, 40.7215, -73.9998, 'Chanel SoHo', 'clothing_store', '139 Spring St, New York, NY 10012', '2024-12-01 15:00:00'),

-- Brunch and Trendy Cafes
(125010, 40.7236, -73.9946, 'Jack''s Wife Freda', 'restaurant', '224 Lafayette St, New York, NY 10012', '2024-12-15 12:30:00'),
(125010, 40.7278, -73.9958, 'Balthazar', 'french_restaurant', '80 Spring St, New York, NY 10012', '2024-12-11 20:00:00'),
(125010, 40.7313, -74.0037, 'Buvette Gastrothèque', 'french_restaurant', '42 Grove St, New York, NY 10014', '2024-12-08 11:00:00'),
(125010, 40.7230, -73.9995, 'Sadelle''s', 'breakfast_restaurant', '463 W Broadway, New York, NY 10012', '2024-12-07 10:30:00'),
(125010, 40.7255, -74.0018, 'La Colombe Coffee Roasters', 'coffee_shop', '400 Lafayette St, New York, NY 10012', '2024-12-05 09:30:00'),
(125010, 40.7236, -73.9946, 'Jack''s Wife Freda', 'restaurant', '224 Lafayette St, New York, NY 10012', '2024-12-01 13:00:00'),

-- Beauty and Wellness
(125010, 40.7222, -73.9985, 'Drybar', 'hair_salon', '4 W 16th St, New York, NY 10011', '2024-12-14 11:00:00'),
(125010, 40.7210, -73.9975, 'Glossier', 'store', '123 Lafayette St, New York, NY 10013', '2024-12-10 18:00:00'),
(125010, 40.7266, -74.0001, 'Paintbox', 'nail_salon', '17 Crosby St, New York, NY 10013', '2024-12-06 17:00:00'),
(125010, 40.7388, -73.9939, 'CorePower Yoga', 'yoga_studio', '32 W 18th St, New York, NY 10011', '2024-12-04 07:00:00'),

-- Arts and Culture
(125010, 40.7230, -73.9930, 'New Museum', 'museum', '235 Bowery, New York, NY 10002', '2024-12-09 15:00:00'),
(125010, 40.7218, -74.0012, 'Jeffrey Deitch', 'art_gallery', '18 Wooster St, New York, NY 10013', '2024-12-03 16:30:00'),
(125010, 40.7261, -74.0008, 'The Drawing Center', 'art_gallery', '35 Wooster St, New York, NY 10013', '2024-11-30 14:00:00');

-- Check-in history for user 125011 (outdoor and sports enthusiast)
-- This user prefers parks, sports facilities, and casual bars, often outside Manhattan.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Parks and Hiking - primary interest, weekends
(125011, 40.6602, -73.9690, 'Prospect Park', 'park', 'Prospect Park, Brooklyn, NY 11225', '2024-12-15 10:00:00'),
(125011, 40.7450, -74.0084, 'Hudson River Park', 'park', 'Hudson River Greenway, New York, NY 10014', '2024-12-14 15:00:00'),
(125011, 40.8662, -73.9189, 'Van Cortlandt Park', 'park', 'Broadway and Van Cortlandt Park S, Bronx, NY 10471', '2024-12-08 09:30:00'),
(125011, 40.7711, -73.9742, 'Central Park Ramble', 'hiking_area', '79th St Transverse, New York, NY 10024', '2024-12-07 11:00:00'),
(125011, 40.5732, -73.9599, 'Coney Island Beach', 'beach', 'Surf Ave, Brooklyn, NY 11224', '2024-12-01 13:00:00'),

-- Sports and Fitness
(125011, 40.6826, -73.9752, 'Barclays Center', 'stadium', '620 Atlantic Ave, Brooklyn, NY 11217', '2024-12-13 19:00:00'),
(125011, 40.7505, -73.9934, 'Madison Square Garden', 'arena', '4 Pennsylvania Plaza, New York, NY 10001', '2024-12-10 19:30:00'),
(125011, 40.6710, -73.9639, 'Prospect Park Tennis Center', 'sports_complex', '50 Parkside Ave, Brooklyn, NY 11226', '2024-12-07 14:00:00'),
(125011, 40.7550, -74.0020, 'Chelsea Piers Sports & Entertainment Complex', 'sports_complex', '62 Chelsea Piers, New York, NY 10011', '2024-12-04 18:30:00'),
(125011, 40.6602, -73.9690, 'Prospect Park Loop', 'cycling_park', 'Prospect Park, Brooklyn, NY 11225', '2024-11-30 08:00:00'),
(125011, 40.7289, -73.9791, 'Blink Fitness', 'gym', '105 1st Ave., New York, NY 10003', '2024-12-16 07:30:00'),
(125011, 40.7289, -73.9791, 'Blink Fitness', 'gym', '105 1st Ave., New York, NY 10003', '2024-12-12 19:00:00'),

-- Shopping for Gear
(125011, 40.7225, -73.9925, 'REI', 'sporting_goods_store', '303 Lafayette St, New York, NY 10012', '2024-12-14 11:00:00'),
(125011, 40.7410, -73.9895, 'Paragon Sports', 'sporting_goods_store', '867 Broadway, New York, NY 10003', '2024-12-06 17:00:00'),
(125011, 40.7145, -73.9575, 'Brooklyn Running Company', 'shoe_store', '222 Grand St, Brooklyn, NY 11211', '2024-12-01 16:00:00'),

-- Casual Dining and Bars
(125011, 40.6780, -73.9720, 'Threes Brewing', 'bar', '333 Douglass St, Brooklyn, NY 11217', '2024-12-15 16:00:00'),
(125011, 40.7681, -73.9585, 'The Pony Bar', 'bar_and_grill', '1444 1st Ave, New York, NY 10021', '2024-12-13 21:30:00'),
(125011, 40.6900, -73.9650, 'Dinosaur Bar-B-Que', 'barbecue_restaurant', '604 Union St, Brooklyn, NY 11215', '2024-12-10 21:00:00'),
(125011, 40.7180, -73.9577, 'The Charleston', 'bar', '174 Bedford Ave, Brooklyn, NY 11249', '2024-12-05 20:00:00'),
(125011, 40.6695, -73.9801, 'Sidecar', 'bar', '560 5th Ave, Brooklyn, NY 11215', '2024-11-30 19:00:00');

-- Check-in history for user 125012 (culinary explorer and foodie)
-- This user's activities are a journey through NYC's diverse food scene, from Queens night markets to fine dining in Manhattan.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Diverse Dining - primary interest
(125012, 40.7484, -73.9857, 'Gramercy Tavern', 'fine_dining_restaurant', '42 E 20th St, New York, NY 10003', '2024-12-14 20:00:00'),
(125012, 40.7490, -73.8550, 'Queens Night Market', 'market', '47-01 111th St, Queens, NY 11368', '2024-12-13 19:30:00'),
(125012, 40.7640, -73.9829, 'Ippudo Westside', 'ramen_restaurant', '321 W 51st St, New York, NY 10019', '2024-12-12 13:00:00'),
(125012, 40.7190, -73.9930, 'Lombardi''s Pizza', 'pizza_restaurant', '32 Spring St, New York, NY 10012', '2024-12-11 18:30:00'),
(125012, 40.7629, -73.9739, 'Totto Ramen', 'ramen_restaurant', '248 E 52nd St, New York, NY 10022', '2024-12-09 21:00:00'),
(125012, 40.7049, -73.9333, 'Roberta''s', 'pizza_restaurant', '261 Moore St, Brooklyn, NY 11206', '2024-12-07 20:30:00'),
(125012, 40.7441, -73.9933, 'Eataly NYC Flatiron', 'market', '200 5th Ave, New York, NY 10010', '2024-12-05 14:00:00'),
(125012, 40.7188, -73.9960, 'Russ & Daughters Cafe', 'deli', '127 Orchard St, New York, NY 10002', '2024-12-03 10:00:00'),
(125012, 40.7580, -73.9855, 'The Halal Guys', 'fast_food_restaurant', 'W 53rd St &, 6th Ave, New York, NY 10019', '2024-12-01 23:30:00'),

-- Food and Drink Preparation/Shopping
(125012, 40.7484, -73.9857, 'Union Square Greenmarket', 'market', 'Union Square W &, E 17th St, New York, NY 10003', '2024-12-14 09:00:00'),
(125012, 40.7305, -73.9927, 'Trader Joe''s', 'grocery_store', '142 E 14th St, New York, NY 10003', '2024-12-10 19:00:00'),
(125012, 40.7877, -73.9775, 'Zabar''s', 'grocery_store', '2245 Broadway, New York, NY 10024', '2024-12-08 11:30:00'),
(125012, 40.7145, -73.9925, 'Kalustyan''s', 'food_store', '123 Lexington Ave, New York, NY 10016', '2024-12-04 17:00:00'),

-- Cafes and Bars
(125012, 40.7259, -73.9975, 'Caffe Reggio', 'cafe', '119 MacDougal St, New York, NY 10012', '2024-12-16 15:00:00'),
(125012, 40.7251, -73.9926, 'The Dead Rabbit', 'bar', '30 Water St, New York, NY 10004', '2024-12-13 23:00:00'),
(125012, 40.7265, -73.9937, 'McSorley''s Old Ale House', 'bar', '15 E 7th St, New York, NY 10003', '2024-12-09 17:00:00'),
(125012, 40.7410, -73.9870, 'Devoción', 'coffee_shop', '25 E 20th St, New York, NY 10003', '2024-12-06 08:45:00'),
(125012, 40.7220, -73.9910, 'Attaboy', 'bar', '134 Eldridge St, New York, NY 10002', '2024-12-02 22:00:00'),

-- Miscellaneous
(125012, 40.7484, -73.9857, 'Madison Square Park', 'park', '11 Madison Ave, New York, NY 10010', '2024-12-14 11:00:00'),
(125012, 40.7420, -74.0048, 'Chelsea Market', 'market', '75 9th Ave, New York, NY 10011', '2024-12-01 13:30:00'),
(125012, 40.7143, -74.0131, 'Oculus', 'shopping_mall', '185 Greenwich St, New York, NY 10007', '2024-11-30 18:00:00');

-- Check-in history for user 125013 (culture and leisure explorer)
-- This user's activities revolve around art, history, performances, and urban relaxation across NYC.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Arts & Culture
(125013, 40.7794, -73.9632, 'The Metropolitan Museum of Art', 'museum', '1000 5th Ave, New York, NY 10028', '2024-12-14 14:00:00'),
(125013, 40.7614, -73.9776, 'Museum of Modern Art (MoMA)', 'museum', '11 W 53rd St, New York, NY 10019', '2024-12-12 16:30:00'),
(125013, 40.7309, -73.9973, 'Blue Note Jazz Club', 'concert_hall', '131 W 3rd St, New York, NY 10012', '2024-12-11 21:00:00'),
(125013, 40.7127, -74.0134, '9/11 Memorial & Museum', 'historical_landmark', '180 Greenwich St, New York, NY 10007', '2024-12-10 11:00:00'),
(125013, 40.7505, -73.9934, 'Madison Square Garden', 'arena', '4 Pennsylvania Plaza, New York, NY 10001', '2024-12-09 19:30:00'),
(125013, 40.7590, -73.9845, 'Broadway Theater District', 'performing_arts_theater', '1681 Broadway, New York, NY 10019', '2024-12-07 20:00:00'),
(125013, 40.7484, -73.9857, 'Empire State Building Observation Deck', 'observation_deck', '20 W 34th St, New York, NY 10001', '2024-12-06 18:15:00'),

-- Parks & Relaxation
(125013, 40.7829, -73.9654, 'Central Park', 'park', 'New York, NY 10024', '2024-12-14 09:30:00'),
(125013, 40.6676, -73.9632, 'Brooklyn Botanic Garden', 'botanical_garden', '990 Washington Ave, Brooklyn, NY 11225', '2024-12-08 15:00:00'),
(125013, 40.7033, -74.0170, 'Battery Park', 'park', 'Battery Park City, New York, NY 10004', '2024-12-05 10:00:00'),

-- Libraries & Learning
(125013, 40.7532, -73.9822, 'New York Public Library - Stephen A. Schwarzman Building', 'library', '476 5th Ave, New York, NY 10018', '2024-12-13 13:00:00'),
(125013, 40.7295, -73.9965, 'NYU Campus', 'university', 'New York University, New York, NY 10003', '2024-12-04 09:30:00'),

-- Nightlife & Entertainment
(125013, 40.7223, -73.9980, 'Bowery Ballroom', 'concert_hall', '6 Delancey St, New York, NY 10002', '2024-12-02 21:30:00'),
(125013, 40.7306, -73.9866, 'Comedy Cellar', 'comedy_club', '117 MacDougal St, New York, NY 10012', '2024-12-01 22:00:00'),

-- Miscellaneous / Attractions
(125013, 40.6892, -74.0445, 'Statue of Liberty National Monument', 'monument', 'Liberty Island, New York, NY 10004', '2024-11-30 12:00:00'),
(125013, 40.7587, -73.9787, 'Rockefeller Center', 'tourist_attraction', '45 Rockefeller Plaza, New York, NY 10111', '2024-11-29 17:00:00'),
(125013, 40.7813, -73.9735, 'American Museum of Natural History', 'museum', '200 Central Park West, New York, NY 10024', '2024-11-28 14:00:00');

-- Check-in history for user 125014 (adventure & outdoor enthusiast)
-- This user's activities mix outdoor adventures, amusement, wildlife, and some cultural exploration across NYC and surroundings.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Adventure & Sports
(125014, 40.7128, -74.0060, 'Chelsea Piers Sports & Entertainment Complex', 'sports_complex', 'Pier 62, New York, NY 10011', '2024-12-15 10:00:00'),
(125014, 40.7810, -73.9665, 'Central Park Cycling Park', 'cycling_park', 'Central Park, New York, NY 10024', '2024-12-14 09:00:00'),
(125014, 40.7531, -73.9832, 'Chelsea Piers Bowling Alley', 'bowling_alley', 'Pier 60, New York, NY 10011', '2024-12-13 15:30:00'),
(125014, 40.7308, -73.9973, 'Hudson River Kayak', 'adventure_sports_center', 'Pier 96, New York, NY 10014', '2024-12-12 11:00:00'),

-- Amusement & Entertainment
(125014, 40.5749, -73.9850, 'Coney Island Luna Park', 'amusement_park', '1000 Surf Ave, Brooklyn, NY 11224', '2024-12-11 13:00:00'),
(125014, 40.5755, -73.9790, 'Coney Island Boardwalk', 'tourist_attraction', 'Brooklyn, NY 11224', '2024-12-11 15:30:00'),
(125014, 40.6310, -73.9440, 'Prospect Park Roller Skating Rink', 'roller_coaster', 'Prospect Park, Brooklyn, NY 11225', '2024-12-10 12:00:00'),
(125014, 40.5840, -73.9740, 'Luna Park Arcade', 'video_arcade', 'Brooklyn, NY 11224', '2024-12-10 14:00:00'),

-- Parks & Hiking
(125014, 40.7851, -73.9683, 'Central Park Great Lawn', 'park', 'Central Park, New York, NY 10024', '2024-12-09 09:00:00'),
(125014, 40.6617, -73.9691, 'Prospect Park', 'park', 'Brooklyn, NY 11225', '2024-12-08 10:30:00'),
(125014, 40.8503, -73.8648, 'Bronx Zoo', 'zoo', '2300 Southern Blvd, Bronx, NY 10460', '2024-12-07 11:00:00'),
(125014, 40.8780, -73.8945, 'Wave Hill Botanical Garden', 'botanical_garden', 'Riverdale, Bronx, NY 10471', '2024-12-06 13:00:00'),

-- Wildlife & Nature
(125014, 40.6980, -73.9620, 'Brooklyn Aquarium', 'aquarium', 'Pier 86, Brooklyn, NY 11201', '2024-12-05 14:00:00'),
(125014, 40.7295, -73.9971, 'Hudson River Park Dog Run', 'dog_park', 'Hudson River Park, New York, NY 10014', '2024-12-04 08:30:00'),
(125014, 40.6740, -73.9712, 'Prospect Park Picnic Ground', 'picnic_ground', 'Brooklyn, NY 11225', '2024-12-03 12:30:00'),

-- Museums & Culture
(125014, 40.7794, -73.9632, 'The Metropolitan Museum of Art', 'museum', '1000 5th Ave, New York, NY 10028', '2024-12-02 14:30:00'),
(125014, 40.7614, -73.9776, 'Museum of Modern Art (MoMA)', 'museum', '11 W 53rd St, New York, NY 10019', '2024-12-01 16:00:00'),
(125014, 40.7484, -73.9857, 'Empire State Building Observation Deck', 'observation_deck', '20 W 34th St, New York, NY 10001', '2024-11-30 18:00:00'),

-- Performance & Entertainment
(125014, 40.7580, -73.9855, 'Broadway Theater District', 'performing_arts_theater', '1681 Broadway, New York, NY 10019', '2024-11-29 20:00:00'),
(125014, 40.7616, -73.9790, 'Radio City Music Hall', 'concert_hall', '1260 6th Ave, New York, NY 10020', '2024-11-28 19:30:00'),

-- Nightlife & Social
(125014, 40.7251, -73.9985, 'McCarren Park Night Club', 'night_club', 'Brooklyn, NY 11222', '2024-11-27 22:00:00'),
(125014, 40.7216, -73.9896, 'Comedy Cellar', 'comedy_club', '117 MacDougal St, New York, NY 10012', '2024-11-26 21:00:00'),

-- Miscellaneous / Tourist Spots
(125014, 40.6892, -74.0445, 'Statue of Liberty National Monument', 'monument', 'Liberty Island, New York, NY 10004', '2024-11-25 11:30:00'),
(125014, 40.7480, -73.9845, 'Madison Square Garden', 'arena', '4 Pennsylvania Plaza, New York, NY 10001', '2024-11-24 18:30:00'),
(125014, 40.7587, -73.9787, 'Rockefeller Center', 'tourist_attraction', '45 Rockefeller Plaza, New York, NY 10111', '2024-11-23 17:00:00'),
(125014, 40.7061, -74.0087, 'Oculus', 'shopping_mall', '185 Greenwich St, New York, NY 10007', '2024-11-22 16:00:00'),
(125014, 40.7425, -74.0047, 'Chelsea Market', 'market', '75 9th Ave, New York, NY 10011', '2024-11-21 14:30:00'),
(125014, 40.7306, -73.9352, 'Queens Night Market', 'market', '47-01 111th St, Queens, NY 11368', '2024-11-20 19:00:00');

-- Check-in history for user 125015 (urban explorer and shopper)
-- This user's activities revolve around shopping, services, and city exploration across NYC.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Shopping Malls & Stores
(125015, 40.7587, -73.9787, 'Rockefeller Center', 'shopping_mall', '45 Rockefeller Plaza, New York, NY 10111', '2024-12-15 16:00:00'),
(125015, 40.7420, -74.0048, 'Chelsea Market', 'market', '75 9th Ave, New York, NY 10011', '2024-12-14 14:00:00'),
(125015, 40.7505, -73.9934, 'Macy''s Herald Square', 'department_store', '151 W 34th St, New York, NY 10001', '2024-12-13 15:30:00'),
(125015, 40.7615, -73.9777, 'Apple Store Fifth Ave', 'electronics_store', '767 5th Ave, New York, NY 10153', '2024-12-12 13:00:00'),
(125015, 40.7624, -73.9750, 'Bloomingdale''s', 'department_store', '1000 3rd Ave, New York, NY 10022', '2024-12-11 14:30:00'),

-- Grocery & Food Stores
(125015, 40.7305, -73.9927, 'Trader Joe''s', 'grocery_store', '142 E 14th St, New York, NY 10003', '2024-12-10 17:00:00'),
(125015, 40.7877, -73.9775, 'Zabar''s', 'grocery_store', '2245 Broadway, New York, NY 10024', '2024-12-09 11:30:00'),
(125015, 40.7145, -73.9925, 'Kalustyan''s', 'food_store', '123 Lexington Ave, New York, NY 10016', '2024-12-08 18:00:00'),
(125015, 40.7484, -73.9857, 'Union Square Greenmarket', 'market', 'Union Square W &, E 17th St, New York, NY 10003', '2024-12-07 10:00:00'),

-- Cafes & Quick Stops
(125015, 40.7259, -73.9975, 'Caffe Reggio', 'cafe', '119 MacDougal St, New York, NY 10012', '2024-12-06 15:00:00'),
(125015, 40.7220, -73.9910, 'Stumptown Coffee Roasters', 'coffee_shop', '18 W 29th St, New York, NY 10001', '2024-12-05 09:30:00'),
(125015, 40.7306, -73.9866, 'Think Coffee', 'coffee_shop', '248 Mercer St, New York, NY 10012', '2024-12-04 10:00:00'),

-- Banks & Services
(125015, 40.7532, -73.9822, 'Chase Bank', 'bank', '270 Park Ave, New York, NY 10017', '2024-12-03 14:00:00'),
(125015, 40.7516, -73.9772, 'Bank of America', 'bank', '100 W 33rd St, New York, NY 10001', '2024-12-02 16:00:00'),
(125015, 40.7580, -73.9855, 'Wells Fargo', 'bank', 'W 50th St, New York, NY 10019', '2024-12-01 11:00:00'),

-- City Exploration / Landmarks
(125015, 40.7484, -73.9857, 'Empire State Building Observation Deck', 'observation_deck', '20 W 34th St, New York, NY 10001', '2024-11-30 17:00:00'),
(125015, 40.7061, -74.0087, 'Oculus', 'shopping_mall', '185 Greenwich St, New York, NY 10007', '2024-11-29 16:00:00'),
(125015, 40.6892, -74.0445, 'Statue of Liberty National Monument', 'monument', 'Liberty Island, New York, NY 10004', '2024-11-28 11:00:00'),
(125015, 40.7580, -73.9855, 'Times Square', 'tourist_attraction', 'Manhattan, NY 10036', '2024-11-27 19:00:00'),
(125015, 40.7411, -73.9897, 'Flatiron Building', 'historical_landmark', '175 5th Ave, New York, NY 10010', '2024-11-26 12:30:00'),

-- Parks & Relaxation
(125015, 40.7829, -73.9654, 'Central Park', 'park', 'New York, NY 10024', '2024-11-25 09:30:00'),
(125015, 40.6676, -73.9632, 'Prospect Park', 'park', 'Brooklyn, NY 11225', '2024-11-24 10:00:00'),

-- Misc / Nightlife
(125015, 40.7251, -73.9926, 'The Dead Rabbit', 'bar', '30 Water St, New York, NY 10004', '2024-11-23 22:00:00'),
(125015, 40.7265, -73.9937, 'McSorley''s Old Ale House', 'bar', '15 E 7th St, New York, NY 10003', '2024-11-22 18:00:00'),

-- Markets & Specialty Stores
(125015, 40.7441, -73.9933, 'Eataly NYC Flatiron', 'market', '200 5th Ave, New York, NY 10010', '2024-11-21 14:00:00'),
(125015, 40.7420, -74.0048, 'Chelsea Market', 'market', '75 9th Ave, New York, NY 10011', '2024-11-20 13:30:00'),
(125015, 40.7490, -73.8550, 'Queens Night Market', 'market', '47-01 111th St, Queens, NY 11368', '2024-11-19 19:00:00'),
(125015, 40.7188, -73.9960, 'Russ & Daughters Cafe', 'deli', '127 Orchard St, New York, NY 10002', '2024-11-18 10:30:00');

-- Check-in history for user 125016 (car enthusiast and traveler)
-- This user's activities revolve around car-related stops, travel, and sightseeing.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Car & Travel Stops
(125016, 40.7580, -73.9855, 'Top Gear Car Wash', 'car_wash', '150 W 52nd St, New York, NY 10019', '2024-12-15 09:00:00'),
(125016, 40.7616, -73.9776, 'EVgo Charging Station', 'electric_vehicle_charging_station', '145 E 55th St, New York, NY 10022', '2024-12-15 09:30:00'),
(125016, 40.7484, -73.9857, 'Empire State Parking Garage', 'parking', '20 W 34th St, New York, NY 10001', '2024-12-15 10:00:00'),
(125016, 40.7306, -73.9957, 'Joe''s Auto Repair', 'car_repair', '98 W 3rd St, New York, NY 10012', '2024-12-14 14:00:00'),
(125016, 40.7527, -73.9772, 'Midtown Car Rental', 'car_rental', '230 Park Ave, New York, NY 10169', '2024-12-14 16:00:00'),

-- Gas & Fuel
(125016, 40.7440, -73.9840, 'Shell Gas Station', 'gas_station', '405 5th Ave, New York, NY 10016', '2024-12-13 08:30:00'),
(125016, 40.7302, -73.9918, 'BP Gas Station', 'gas_station', '112 E 14th St, New York, NY 10003', '2024-12-13 09:00:00'),
(125016, 40.7611, -73.9800, 'Tesla Supercharger', 'electric_vehicle_charging_station', '100 E 57th St, New York, NY 10022', '2024-12-12 17:00:00'),

-- Tourist Stops
(125016, 40.6892, -74.0445, 'Statue of Liberty', 'monument', 'Liberty Island, New York, NY 10004', '2024-12-11 11:30:00'),
(125016, 40.7484, -73.9857, 'Empire State Building Observation Deck', 'observation_deck', '20 W 34th St, New York, NY 10001', '2024-12-11 13:30:00'),
(125016, 40.7580, -73.9855, 'Times Square', 'tourist_attraction', 'Manhattan, NY 10036', '2024-12-11 15:00:00'),

-- Rest Stops & Convenience
(125016, 40.7505, -73.9934, 'Penn Station Parking', 'parking', 'New York, NY 10121', '2024-12-10 09:00:00'),
(125016, 40.7561, -73.9903, 'Rest Stop - Midtown', 'rest_stop', 'New York, NY 10001', '2024-12-10 09:30:00'),
(125016, 40.7480, -73.9840, '5th Ave Gas & Coffee', 'gas_station', 'New York, NY 10001', '2024-12-09 08:30:00'),

-- Car Dealerships
(125016, 40.7612, -73.9770, 'Manhattan Motors', 'car_dealer', '123 E 57th St, New York, NY 10022', '2024-12-08 11:00:00'),
(125016, 40.7620, -73.9735, 'Luxury Auto Gallery', 'car_dealer', '987 3rd Ave, New York, NY 10022', '2024-12-08 12:00:00'),

-- Cultural / Attractions
(125016, 40.7794, -73.9632, 'The Metropolitan Museum of Art', 'museum', '1000 5th Ave, New York, NY 10028', '2024-12-07 14:00:00'),
(125016, 40.7061, -74.0087, 'Oculus', 'shopping_mall', '185 Greenwich St, New York, NY 10007', '2024-12-06 16:00:00'),

-- Nightlife / Bars for social stops
(125016, 40.7251, -73.9926, 'The Dead Rabbit', 'bar', '30 Water St, New York, NY 10004', '2024-12-05 21:00:00'),
(125016, 40.7265, -73.9937, 'McSorley''s Old Ale House', 'bar', '15 E 7th St, New York, NY 10003', '2024-12-05 19:00:00'),

-- Misc / Markets & Shopping
(125016, 40.7420, -74.0048, 'Chelsea Market', 'market', '75 9th Ave, New York, NY 10011', '2024-12-04 15:00:00'),
(125016, 40.7490, -73.8550, 'Queens Night Market', 'market', '47-01 111th St, Queens, NY 11368', '2024-12-03 18:00:00'),
(125016, 40.7441, -73.9933, 'Eataly NYC Flatiron', 'market', '200 5th Ave, New York, NY 10010', '2024-12-02 14:00:00'),

-- Parking / Quick Stops
(125016, 40.7584, -73.9857, 'Midtown Parking Garage', 'parking', 'New York, NY 10019', '2024-12-01 09:00:00'),
(125016, 40.7305, -73.9912, 'Village Parking', 'parking', 'New York, NY 10012', '2024-11-30 10:30:00');

-- Check-in history for user 125017 (family & leisure focused)
-- This user's activities revolve around outdoor fun, amusement, and kid-friendly spots.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Amusement & Parks
(125017, 40.5749, -73.9850, 'Coney Island Luna Park', 'amusement_park', '1000 Surf Ave, Brooklyn, NY 11224', '2024-12-15 11:00:00'),
(125017, 40.5745, -73.9835, 'Coney Island Boardwalk', 'tourist_attraction', 'Brooklyn, NY 11224', '2024-12-15 12:30:00'),
(125017, 40.6310, -73.9440, 'Prospect Park Roller Skating Rink', 'roller_coaster', 'Prospect Park, Brooklyn, NY 11225', '2024-12-14 10:00:00'),
(125017, 40.6750, -73.9700, 'Prospect Park Playground', 'playground', 'Brooklyn, NY 11225', '2024-12-14 11:30:00'),

-- Wildlife & Animal Encounters
(125017, 40.8503, -73.8648, 'Bronx Zoo', 'zoo', '2300 Southern Blvd, Bronx, NY 10460', '2024-12-13 09:30:00'),
(125017, 40.6980, -73.9620, 'Brooklyn Aquarium', 'aquarium', 'Pier 86, Brooklyn, NY 11201', '2024-12-13 11:00:00'),
(125017, 40.8780, -73.8945, 'Wave Hill Botanical Garden', 'botanical_garden', 'Riverdale, Bronx, NY 10471', '2024-12-12 14:00:00'),
(125017, 40.7305, -73.9352, 'Queens Wildlife Refuge', 'wildlife_refuge', 'Queens, NY 11368', '2024-12-12 12:30:00'),

-- Adventure & Sports
(125017, 40.7128, -74.0060, 'Hudson River Kayak', 'adventure_sports_center', 'Pier 96, New York, NY 10014', '2024-12-11 10:00:00'),
(125017, 40.7580, -73.9855, 'Chelsea Piers Sports Complex', 'sports_complex', 'Pier 62, New York, NY 10011', '2024-12-11 13:00:00'),
(125017, 40.7810, -73.9665, 'Central Park Cycling Park', 'cycling_park', 'Central Park, New York, NY 10024', '2024-12-10 09:00:00'),
(125017, 40.7420, -74.0048, 'Chelsea Piers Bowling Alley', 'bowling_alley', '75 9th Ave, New York, NY 10011', '2024-12-10 12:00:00'),

-- Camping & Outdoor Relaxation
(125017, 40.7000, -73.9000, 'Brooklyn Campground', 'campground', 'Brooklyn, NY 11206', '2024-12-09 15:00:00'),
(125017, 40.7050, -73.9200, 'Brooklyn Camping Cabin', 'camping_cabin', 'Brooklyn, NY 11206', '2024-12-09 16:30:00'),
(125017, 40.7851, -73.9683, 'Central Park Picnic Ground', 'picnic_ground', 'Central Park, NY 10024', '2024-12-08 11:00:00'),
(125017, 40.6676, -73.9632, 'Prospect Park Picnic Ground', 'picnic_ground', 'Brooklyn, NY 11225', '2024-12-08 12:30:00'),

-- Play & Entertainment Centers
(125017, 40.7540, -73.9840, 'Fun Central Video Arcade', 'video_arcade', 'Manhattan, NY 10001', '2024-12-07 10:30:00'),
(125017, 40.7550, -73.9800, 'Sky High Indoor Playground', 'children_camp', 'Manhattan, NY 10001', '2024-12-07 12:00:00'),
(125017, 40.7420, -74.0048, 'Chelsea Indoor Amusement Center', 'amusement_center', '75 9th Ave, New York, NY 10011', '2024-12-06 13:00:00'),

-- Aquatic Fun
(125017, 40.6315, -73.9330, 'Brooklyn Water Park', 'water_park', 'Brooklyn, NY 11206', '2024-12-05 11:30:00'),
(125017, 40.6320, -73.9350, 'Aquatic Adventure Center', 'adventure_sports_center', 'Brooklyn, NY 11206', '2024-12-05 13:00:00'),

-- Misc / Family-Friendly Markets & Stops
(125017, 40.7441, -73.9933, 'Eataly NYC Flatiron', 'market', '200 5th Ave, New York, NY 10010', '2024-12-04 10:00:00'),
(125017, 40.7490, -73.8550, 'Queens Night Market', 'market', '47-01 111th St, Queens, NY 11368', '2024-12-04 12:00:00'),
(125017, 40.7420, -74.0048, 'Chelsea Market', 'market', '75 9th Ave, New York, NY 10011', '2024-12-03 11:30:00'),

-- Parks & Dog-Friendly Stops
(125017, 40.7305, -73.9971, 'Hudson River Park Dog Run', 'dog_park', 'Hudson River Park, New York, NY 10014', '2024-12-02 09:30:00'),
(125017, 40.6675, -73.9712, 'Prospect Park Dog Park', 'dog_park', 'Brooklyn, NY 11225', '2024-12-02 11:00:00');

-- Check-in history for user 125018 (daytime entertainment & foodie)
-- This user's activities revolve around cafes, bakeries, markets, casual restaurants, and daytime leisure.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Cafes & Coffee Shops
(125018, 40.7259, -73.9975, 'Caffe Reggio', 'cafe', '119 MacDougal St, New York, NY 10012', '2024-12-15 10:00:00'),
(125018, 40.7306, -73.9866, 'Think Coffee', 'coffee_shop', '248 Mercer St, New York, NY 10012', '2024-12-15 11:00:00'),
(125018, 40.7220, -73.9910, 'Stumptown Coffee Roasters', 'coffee_shop', '18 W 29th St, New York, NY 10001', '2024-12-14 09:30:00'),

-- Bakeries & Dessert Shops
(125018, 40.7225, -73.9980, 'Dominique Ansel Bakery', 'bakery', '189 Spring St, New York, NY 10012', '2024-12-14 10:30:00'),
(125018, 40.7230, -73.9975, 'Milk Bar', 'dessert_shop', '220 7th Ave S, New York, NY 10014', '2024-12-13 11:00:00'),
(125018, 40.7320, -73.9990, 'Baked by Melissa', 'dessert_shop', '200 W 39th St, New York, NY 10018', '2024-12-13 11:30:00'),

-- Brunch & Casual Restaurants
(125018, 40.7410, -73.9890, 'Jack''s Wife Freda', 'brunch_restaurant', '224 Lafayette St, New York, NY 10012', '2024-12-12 12:00:00'),
(125018, 40.7420, -73.9850, 'Clinton St. Baking Company', 'brunch_restaurant', '4 Clinton St, New York, NY 10002', '2024-12-12 12:30:00'),
(125018, 40.7305, -73.9950, 'Ruby''s Cafe', 'brunch_restaurant', '219 Mulberry St, New York, NY 10012', '2024-12-11 11:30:00'),

-- Markets & Food Stores
(125018, 40.7420, -74.0048, 'Chelsea Market', 'market', '75 9th Ave, New York, NY 10011', '2024-12-11 13:00:00'),
(125018, 40.7441, -73.9933, 'Eataly NYC Flatiron', 'market', '200 5th Ave, New York, NY 10010', '2024-12-10 14:00:00'),
(125018, 40.7490, -73.8550, 'Queens Night Market', 'market', '47-01 111th St, Queens, NY 11368', '2024-12-10 15:30:00'),

-- Movie Theaters & Cinemas
(125018, 40.7560, -73.9860, 'AMC Empire 25', 'movie_theater', '234 W 42nd St, New York, NY 10036', '2024-12-09 14:00:00'),
(125018, 40.7590, -73.9855, 'Regal E-Walk 13', 'movie_theater', '247 W 42nd St, New York, NY 10036', '2024-12-09 15:30:00'),
(125018, 40.7310, -73.9970, 'IFC Center', 'movie_theater', '323 6th Ave, New York, NY 10014', '2024-12-08 13:00:00'),

-- Parks & Outdoor Relaxation
(125018, 40.7829, -73.9654, 'Central Park', 'park', 'New York, NY 10024', '2024-12-08 10:00:00'),
(125018, 40.6676, -73.9632, 'Prospect Park', 'park', 'Brooklyn, NY 11225', '2024-12-07 09:30:00'),
(125018, 40.7484, -73.9857, 'Madison Square Park', 'park', '11 Madison Ave, New York, NY 10010', '2024-12-07 11:00:00'),

-- Specialty Shops
(125018, 40.7188, -73.9960, 'Russ & Daughters Cafe', 'deli', '127 Orchard St, New York, NY 10002', '2024-12-06 10:00:00'),
(125018, 40.7305, -73.9927, 'Trader Joe''s', 'grocery_store', '142 E 14th St, New York, NY 10003', '2024-12-06 11:30:00'),
(125018, 40.7877, -73.9775, 'Zabar''s', 'grocery_store', '2245 Broadway, New York, NY 10024', '2024-12-05 09:30:00'),
(125018, 40.7145, -73.9925, 'Kalustyan''s', 'food_store', '123 Lexington Ave, New York, NY 10016', '2024-12-05 12:00:00'),

-- Coffee Shops & Light Stops
(125018, 40.7250, -73.9960, 'Birch Coffee', 'coffee_shop', '21 E 27th St, New York, NY 10016', '2024-12-04 09:00:00'),
(125018, 40.7410, -73.9870, 'Devoción', 'coffee_shop', '25 E 20th St, New York, NY 10003', '2024-12-04 10:00:00'),
(125018, 40.7440, -73.9950, 'Blue Bottle Coffee', 'coffee_shop', '450 W 15th St, New York, NY 10011', '2024-12-03 11:00:00'),

-- Casual Brunch / Lunch
(125018, 40.7255, -73.9985, 'Sadelle''s', 'brunch_restaurant', '463 W Broadway, New York, NY 10012', '2024-12-03 12:30:00'),
(125018, 40.7300, -73.9920, 'The Smith', 'brunch_restaurant', '55 3rd Ave, New York, NY 10003', '2024-12-02 12:00:00'),
(125018, 40.7415, -73.9890, 'Maison Kayser', 'bakery', '8 W 40th St, New York, NY 10018', '2024-12-02 09:30:00');

-- Check-in history for user 125019 (road-tripper and car enthusiast)
-- This user's activities revolve around driving, refueling, and quick casual stops.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Car & Travel Stops
(125019, 40.7484, -73.9857, 'Empire State Parking Garage', 'parking', '20 W 34th St, New York, NY 10001', '2024-12-15 08:30:00'),
(125019, 40.7616, -73.9776, 'EVgo Charging Station', 'electric_vehicle_charging_station', '145 E 55th St, New York, NY 10022', '2024-12-15 09:00:00'),
(125019, 40.7580, -73.9855, 'Top Gear Car Wash', 'car_wash', '150 W 52nd St, New York, NY 10019', '2024-12-14 10:00:00'),
(125019, 40.7306, -73.9957, 'Joe''s Auto Repair', 'car_repair', '98 W 3rd St, New York, NY 10012', '2024-12-14 14:00:00'),
(125019, 40.7527, -73.9772, 'Midtown Car Rental', 'car_rental', '230 Park Ave, New York, NY 10169', '2024-12-14 16:00:00'),

-- Fuel Stops
(125019, 40.7440, -73.9840, 'Shell Gas Station', 'gas_station', '405 5th Ave, New York, NY 10016', '2024-12-13 08:00:00'),
(125019, 40.7302, -73.9918, 'BP Gas Station', 'gas_station', '112 E 14th St, New York, NY 10003', '2024-12-13 08:30:00'),
(125019, 40.7611, -73.9800, 'Tesla Supercharger', 'electric_vehicle_charging_station', '100 E 57th St, New York, NY 10022', '2024-12-12 17:00:00'),

-- Quick Food Stops
(125019, 40.7220, -73.9910, 'Shake Shack', 'fast_food_restaurant', 'Madison Square Park, NY 10010', '2024-12-12 12:00:00'),
(125019, 40.7188, -73.9960, 'Russ & Daughters Cafe', 'deli', '127 Orchard St, New York, NY 10002', '2024-12-11 09:00:00'),
(125019, 40.7420, -74.0048, 'Chelsea Market', 'market', '75 9th Ave, New York, NY 10011', '2024-12-11 13:30:00'),

-- Rest & Convenience Stops
(125019, 40.7505, -73.9934, 'Penn Station Parking', 'parking', 'New York, NY 10121', '2024-12-10 09:00:00'),
(125019, 40.7561, -73.9903, 'Midtown Rest Stop', 'rest_stop', 'New York, NY 10001', '2024-12-10 09:30:00'),
(125019, 40.7480, -73.9840, '5th Ave Gas & Coffee', 'gas_station', 'New York, NY 10001', '2024-12-09 08:30:00'),

-- Car Dealerships & Auto Shops
(125019, 40.7612, -73.9770, 'Manhattan Motors', 'car_dealer', '123 E 57th St, New York, NY 10022', '2024-12-08 11:00:00'),
(125019, 40.7620, -73.9735, 'Luxury Auto Gallery', 'car_dealer', '987 3rd Ave, New York, NY 10022', '2024-12-08 12:00:00'),

-- Family-Friendly Quick Stops
(125019, 40.7305, -73.9927, 'Trader Joe''s', 'grocery_store', '142 E 14th St, New York, NY 10003', '2024-12-07 10:00:00'),
(125019, 40.7877, -73.9775, 'Zabar''s', 'grocery_store', '2245 Broadway, New York, NY 10024', '2024-12-07 11:30:00'),
(125019, 40.7441, -73.9933, 'Eataly NYC Flatiron', 'market', '200 5th Ave, New York, NY 10010', '2024-12-06 12:00:00'),

-- Parks & Outdoor Stops
(125019, 40.7829, -73.9654, 'Central Park', 'park', 'New York, NY 10024', '2024-12-06 09:00:00'),
(125019, 40.6676, -73.9632, 'Prospect Park', 'park', 'Brooklyn, NY 11225', '2024-12-05 09:30:00'),

-- Quick Casual Dining / Cafes
(125019, 40.7259, -73.9975, 'Caffe Reggio', 'cafe', '119 MacDougal St, New York, NY 10012', '2024-12-05 10:30:00'),
(125019, 40.7306, -73.9866, 'Think Coffee', 'coffee_shop', '248 Mercer St, New York, NY 10012', '2024-12-04 11:00:00'),
(125019, 40.7225, -73.9980, 'Dominique Ansel Bakery', 'bakery', '189 Spring St, New York, NY 10012', '2024-12-04 10:30:00'),
(125019, 40.7230, -73.9975, 'Milk Bar', 'dessert_shop', '220 7th Ave S, New York, NY 10014', '2024-12-03 11:00:00'),
(125019, 40.7320, -73.9990, 'Baked by Melissa', 'dessert_shop', '200 W 39th St, New York, NY 10018', '2024-12-03 11:30:00');

-- Check-in history for user 125020 (Nature & Outdoor Explorer)
-- This user's activities revolve around hiking, parks, botanical gardens, wildlife refuges, and casual outdoor stops.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Parks & Outdoor Areas
(125020, 40.7829, -73.9654, 'Central Park', 'park', 'New York, NY 10024', '2024-12-15 08:00:00'),
(125020, 40.6676, -73.9632, 'Prospect Park', 'park', 'Brooklyn, NY 11225', '2024-12-15 09:00:00'),
(125020, 40.7484, -73.9857, 'Madison Square Park', 'park', '11 Madison Ave, New York, NY 10010', '2024-12-14 10:00:00'),

-- Botanical & Gardens
(125020, 40.6694, -73.9627, 'Brooklyn Botanic Garden', 'botanical_garden', '990 Washington Ave, Brooklyn, NY 11225', '2024-12-14 11:30:00'),
(125020, 40.7812, -73.9665, 'Conservatory Garden', 'garden', '5th Ave & 105th St, New York, NY 10029', '2024-12-13 09:00:00'),
(125020, 40.6678, -73.9715, 'Green-Wood Cemetery Gardens', 'garden', '500 25th St, Brooklyn, NY 11232', '2024-12-13 10:30:00'),

-- Hiking & Walking Areas
(125020, 40.8681, -73.9152, 'Van Cortlandt Park Hiking Trails', 'hiking_area', 'Bronx, NY 10471', '2024-12-12 08:30:00'),
(125020, 40.8500, -73.8662, 'Bronx River Greenway', 'cycling_park', 'Bronx, NY 10462', '2024-12-12 10:00:00'),
(125020, 40.7730, -73.9700, 'Riverside Park', 'park', 'New York, NY 10024', '2024-12-11 09:00:00'),

-- Wildlife & Nature
(125020, 40.7813, -73.9735, 'Central Park Zoo', 'zoo', 'East 64th St, New York, NY 10021', '2024-12-11 11:00:00'),
(125020, 40.8690, -73.8665, 'Bronx Zoo', 'zoo', '2300 Southern Blvd, Bronx, NY 10460', '2024-12-10 09:30:00'),
(125020, 40.6976, -73.9935, 'Prospect Park Zoo', 'zoo', '450 Flatbush Ave, Brooklyn, NY 11225', '2024-12-10 11:00:00'),
(125020, 40.6740, -73.9650, 'Brooklyn Wildlife Refuge', 'wildlife_refuge', 'Brooklyn, NY 11225', '2024-12-09 08:30:00'),

-- Picnic & Leisure Areas
(125020, 40.7480, -73.9845, 'Madison Square Park Picnic Grounds', 'picnic_ground', 'New York, NY 10010', '2024-12-09 12:00:00'),
(125020, 40.7690, -73.9817, 'Riverside Park Picnic Area', 'picnic_ground', 'New York, NY 10024', '2024-12-08 12:30:00'),
(125020, 40.7300, -73.9950, 'Washington Square Park', 'park', 'New York, NY 10012', '2024-12-08 10:00:00'),

-- Nature Walks & Trails
(125020, 40.8670, -73.9150, 'Pinehurst Lake Trail', 'hiking_area', 'Bronx, NY 10471', '2024-12-07 08:00:00'),
(125020, 40.8510, -73.8670, 'Soundview Park Trails', 'hiking_area', 'Bronx, NY 10473', '2024-12-07 09:30:00'),

-- Casual Food / Juice Shops near Outdoor Areas
(125020, 40.7820, -73.9650, 'Juice Press - Central Park', 'juice_shop', 'New York, NY 10024', '2024-12-06 10:00:00'),
(125020, 40.6670, -73.9620, 'Brooklyn Green Cafe', 'cafe', 'Brooklyn, NY 11225', '2024-12-06 11:30:00'),
(125020, 40.7440, -73.9950, 'Eataly NYC Flatiron', 'market', '200 5th Ave, New York, NY 10010', '2024-12-05 12:00:00'),

-- More Parks & Recreation
(125020, 40.7680, -73.9810, 'Morningside Park', 'park', 'New York, NY 10027', '2024-12-05 09:00:00'),
(125020, 40.7310, -73.9960, 'Hudson River Park', 'park', 'New York, NY 10014', '2024-12-04 08:30:00'),
(125020, 40.7280, -73.9950, 'Brooklyn Bridge Park', 'park', 'Brooklyn, NY 11201', '2024-12-04 10:00:00'),

-- Botanical & Nature Spots
(125020, 40.7290, -73.9960, 'Union Square Greenmarket', 'market', 'New York, NY 10003', '2024-12-03 11:00:00'),
(125020, 40.7340, -73.9910, 'Madison Square Garden Gardens', 'garden', 'New York, NY 10010', '2024-12-03 12:30:00'),
(125020, 40.7285, -73.9955, 'Green-Wood Arboretum', 'garden', 'Brooklyn, NY 11232', '2024-12-02 09:00:00');


-- Check-in history for user 125021 (Tech & Gadgets Fan)
-- This user's activities revolve around electronics stores, gadget shops, coworking spaces, and tech-focused venues.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Electronics & Gadget Stores
(125021, 40.7532, -73.9830, 'B&H Photo Video', 'electronics_store', '420 9th Ave, New York, NY 10001', '2024-12-15 10:00:00'),
(125021, 40.7615, -73.9773, 'Apple Store Fifth Ave', 'electronics_store', '767 5th Ave, New York, NY 10153', '2024-12-15 11:30:00'),
(125021, 40.7420, -73.9897, 'Adorama', 'electronics_store', '42 W 18th St, New York, NY 10011', '2024-12-14 10:00:00'),
(125021, 40.7579, -73.9855, 'Best Buy Midtown', 'electronics_store', '529 5th Ave, New York, NY 10017', '2024-12-14 13:00:00'),

-- Maker Spaces & Tech Labs
(125021, 40.7280, -73.9950, 'NYC Resistor', 'community_center', '87 2nd Ave, Brooklyn, NY 11215', '2024-12-13 09:30:00'),
(125021, 40.7295, -73.9970, 'Fat Cat Maker Space', 'community_center', '75 Washington Pl, New York, NY 10003', '2024-12-13 11:00:00'),
(125021, 40.7320, -73.9950, 'MakerBot Store', 'electronics_store', '298 Mulberry St, New York, NY 10012', '2024-12-12 10:30:00'),

-- Gaming & VR Lounges
(125021, 40.7580, -73.9855, 'VR World NYC', 'amusement_center', '8 E 34th St, New York, NY 10016', '2024-12-12 14:00:00'),
(125021, 40.7610, -73.9790, 'Barcade NYC', 'video_arcade', '148 W 24th St, New York, NY 10011', '2024-12-11 13:30:00'),

-- Coworking Spaces & Tech Hubs
(125021, 40.7410, -73.9890, 'WeWork Flatiron', 'office', '115 W 18th St, New York, NY 10011', '2024-12-11 09:00:00'),
(125021, 40.7520, -73.9815, 'Industrious Midtown', 'office', '110 E 42nd St, New York, NY 10017', '2024-12-10 10:30:00'),
(125021, 40.7305, -73.9950, 'Brooklyn Tech Hub', 'office', '120 Lafayette Ave, Brooklyn, NY 11216', '2024-12-10 11:30:00'),

-- Tech Expos & Conferences
(125021, 40.7570, -73.9860, 'Tech Expo NYC', 'convention_center', '429 5th Ave, New York, NY 10016', '2024-12-09 09:00:00'),
(125021, 40.7585, -73.9810, 'Innovation Summit', 'convention_center', '520 5th Ave, New York, NY 10036', '2024-12-09 12:00:00'),

-- Casual Cafes / Breaks
(125021, 40.7305, -73.9950, 'Think Coffee', 'coffee_shop', '248 Mercer St, New York, NY 10012', '2024-12-08 10:00:00'),
(125021, 40.7259, -73.9975, 'Caffe Reggio', 'cafe', '119 MacDougal St, New York, NY 10012', '2024-12-08 11:00:00'),
(125021, 40.7420, -73.9880, 'Blue Bottle Coffee', 'coffee_shop', '1 Rockefeller Plaza, New York, NY 10020', '2024-12-07 09:30:00'),

-- Electronics & Accessories Shops
(125021, 40.7540, -73.9840, 'J&R Music and Computer World', 'electronics_store', '1 Park Row, New York, NY 10038', '2024-12-07 14:00:00'),
(125021, 40.7530, -73.9815, 'Micro Center', 'electronics_store', '850 5th Ave, New York, NY 10065', '2024-12-06 13:00:00'),

-- Casual Food / Quick Snacks
(125021, 40.7420, -74.0048, 'Chelsea Market', 'market', '75 9th Ave, New York, NY 10011', '2024-12-06 12:00:00'),
(125021, 40.7441, -73.9933, 'Eataly NYC Flatiron', 'market', '200 5th Ave, New York, NY 10010', '2024-12-05 12:30:00'),

-- Parks & Relaxation
(125021, 40.7829, -73.9654, 'Central Park', 'park', 'New York, NY 10024', '2024-12-05 09:00:00'),
(125021, 40.6676, -73.9632, 'Prospect Park', 'park', 'Brooklyn, NY 11225', '2024-12-04 09:30:00'),

-- Libraries / Study Spaces
(125021, 40.7532, -73.9822, 'NY Public Library - Science Center', 'library', '476 5th Ave, New York, NY 10018', '2024-12-04 11:00:00'),
(125021, 40.7535, -73.9835, 'NYPL Research Library', 'library', '476 5th Ave, New York, NY 10018', '2024-12-03 10:00:00');

 -- Check-in history for user 125022 (Shopping & Fashionista)
-- This user's activities revolve around shopping malls, clothing stores, shoe stores, jewelry shops, and fashion boutiques.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Shopping Malls & Department Stores
(125022, 40.7625, -73.9731, 'Bloomingdale''s', 'department_store', '1000 3rd Ave, New York, NY 10022', '2024-12-15 11:00:00'),
(125022, 40.7620, -73.9740, 'Macy''s Herald Square', 'department_store', '151 W 34th St, New York, NY 10001', '2024-12-15 13:00:00'),
(125022, 40.7585, -73.9780, 'Saks Fifth Avenue', 'department_store', '611 5th Ave, New York, NY 10022', '2024-12-14 12:00:00'),

-- Clothing Stores & Boutiques
(125022, 40.7400, -73.9880, 'Zara Flatiron', 'clothing_store', '123 5th Ave, New York, NY 10010', '2024-12-14 10:00:00'),
(125022, 40.7430, -73.9910, 'Uniqlo Flatiron', 'clothing_store', '31 E 17th St, New York, NY 10003', '2024-12-13 11:00:00'),
(125022, 40.7610, -73.9770, 'H&M Midtown', 'clothing_store', '115 W 34th St, New York, NY 10120', '2024-12-13 12:30:00'),

-- Shoe Stores
(125022, 40.7620, -73.9750, 'Nike Store', 'shoe_store', '650 5th Ave, New York, NY 10019', '2024-12-12 10:30:00'),
(125022, 40.7580, -73.9800, 'Adidas Store', 'shoe_store', '500 5th Ave, New York, NY 10036', '2024-12-12 11:30:00'),
(125022, 40.7615, -73.9735, 'Foot Locker', 'shoe_store', '30 W 34th St, New York, NY 10001', '2024-12-11 12:00:00'),

-- Jewelry Stores
(125022, 40.7625, -73.9745, 'Tiffany & Co.', 'jewelry_store', '727 5th Ave, New York, NY 10022', '2024-12-11 13:00:00'),
(125022, 40.7585, -73.9785, 'Cartier', 'jewelry_store', '653 5th Ave, New York, NY 10022', '2024-12-10 11:30:00'),
(125022, 40.7620, -73.9755, 'Harry Winston', 'jewelry_store', '718 5th Ave, New York, NY 10022', '2024-12-10 12:30:00'),

-- Boutique / Fashion Stores
(125022, 40.7410, -73.9890, 'Madewell', 'clothing_store', '115 W 23rd St, New York, NY 10011', '2024-12-09 10:00:00'),
(125022, 40.7425, -73.9885, 'Anthropologie', 'clothing_store', '28 E 23rd St, New York, NY 10010', '2024-12-09 11:00:00'),
(125022, 40.7430, -73.9870, 'J.Crew', 'clothing_store', '160 5th Ave, New York, NY 10010', '2024-12-08 10:30:00'),

-- Shopping Centers & Markets
(125022, 40.7420, -74.0048, 'Chelsea Market', 'market', '75 9th Ave, New York, NY 10011', '2024-12-08 12:00:00'),
(125022, 40.7441, -73.9933, 'Eataly NYC Flatiron', 'market', '200 5th Ave, New York, NY 10010', '2024-12-07 12:30:00'),
(125022, 40.7595, -73.9790, 'The Shops at Columbus Circle', 'shopping_mall', '10 Columbus Circle, New York, NY 10019', '2024-12-07 13:00:00'),

-- Casual Cafes & Juice Bars Near Shopping Areas
(125022, 40.7415, -73.9885, 'Bluestone Lane Cafe', 'cafe', '55 W 23rd St, New York, NY 10010', '2024-12-06 10:00:00'),
(125022, 40.7420, -73.9875, 'Joe Coffee Company', 'coffee_shop', '141 W 23rd St, New York, NY 10011', '2024-12-06 11:00:00'),
(125022, 40.7430, -73.9890, 'Juice Press', 'juice_shop', '36 W 23rd St, New York, NY 10010', '2024-12-05 10:30:00'),

-- More Malls & Department Stores
(125022, 40.7580, -73.9855, 'Bloomingdale''s Soho', 'department_store', '504 Broadway, New York, NY 10012', '2024-12-05 12:00:00'),
(125022, 40.7590, -73.9800, 'Barneys New York', 'department_store', '660 Madison Ave, New York, NY 10065', '2024-12-04 13:00:00'),

-- Fashion Boutiques / Accessories
(125022, 40.7425, -73.9870, 'Kate Spade', 'clothing_store', '100 5th Ave, New York, NY 10011', '2024-12-04 10:00:00'),
(125022, 40.7430, -73.9865, 'Coach', 'clothing_store', '10 W 23rd St, New York, NY 10010', '2024-12-03 10:30:00'),
(125022, 40.7410, -73.9895, 'Michael Kors', 'clothing_store', '489 5th Ave, New York, NY 10017', '2024-12-03 11:00:00');


-- Check-in history for user 125023 (Food Truck & Street Food Explorer)
-- This user's activities revolve around street food, casual markets, dessert shops, and quick bites with some light leisure stops.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Street Food & Food Trucks
(125023, 40.7420, -73.9890, 'Halal Guys Food Cart', 'fast_food_restaurant', 'W 53rd St & 6th Ave, New York, NY 10019', '2024-12-15 12:30:00'),
(125023, 40.7280, -73.9970, 'Taco Truck - East Village', 'mexican_restaurant', '1st Ave & 9th St, New York, NY 10009', '2024-12-15 13:00:00'),
(125023, 40.7310, -73.9920, 'Waffle Truck', 'dessert_shop', 'Broadway & 14th St, New York, NY 10001', '2024-12-14 11:00:00'),
(125023, 40.7510, -73.9810, 'NYC Pizza Slice Truck', 'pizza_restaurant', '7th Ave & 33rd St, New York, NY 10001', '2024-12-14 12:00:00'),
(125023, 40.7425, -74.0030, 'Hot Dog Cart', 'fast_food_restaurant', 'Chelsea, NY 10011', '2024-12-13 13:30:00'),

-- Markets & Casual Food Stops
(125023, 40.7420, -74.0048, 'Chelsea Market', 'market', '75 9th Ave, New York, NY 10011', '2024-12-13 10:30:00'),
(125023, 40.7441, -73.9933, 'Eataly NYC Flatiron', 'market', '200 5th Ave, New York, NY 10010', '2024-12-12 12:00:00'),
(125023, 40.7280, -73.9940, 'Union Square Greenmarket', 'market', 'Union Square W & E 17th St, New York, NY 10003', '2024-12-12 09:30:00'),

-- Dessert & Specialty Shops
(125023, 40.7190, -73.9980, 'Magnolia Bakery', 'dessert_shop', '401 Bleecker St, New York, NY 10014', '2024-12-11 11:00:00'),
(125023, 40.7250, -73.9935, 'Levain Bakery', 'bakery', '167 W 74th St, New York, NY 10023', '2024-12-11 12:00:00'),
(125023, 40.7225, -73.9980, 'ChocoMania', 'chocolate_shop', 'Greenwich St, New York, NY 10013', '2024-12-10 10:30:00'),

-- Casual Cafes & Juice Shops
(125023, 40.7305, -73.9950, 'Think Coffee', 'coffee_shop', '248 Mercer St, New York, NY 10012', '2024-12-10 09:00:00'),
(125023, 40.7425, -73.9870, 'Bluestone Lane Cafe', 'cafe', '55 W 23rd St, New York, NY 10010', '2024-12-09 10:00:00'),
(125023, 40.7410, -73.9885, 'Joe Coffee Company', 'coffee_shop', '141 W 23rd St, New York, NY 10011', '2024-12-09 11:00:00'),

-- Light Parks & Leisure
(125023, 40.7300, -73.9950, 'Washington Square Park', 'park', 'New York, NY 10012', '2024-12-08 09:30:00'),
(125023, 40.7829, -73.9654, 'Central Park', 'park', 'New York, NY 10024', '2024-12-08 11:30:00'),
(125023, 40.6676, -73.9632, 'Prospect Park', 'park', 'Brooklyn, NY 11225', '2024-12-07 10:00:00'),

-- International Street Food & Specialty Cuisine
(125023, 40.7590, -73.9810, 'Thai Street Food Truck', 'thai_restaurant', 'Midtown, NY 10019', '2024-12-07 12:30:00'),
(125023, 40.7480, -73.9855, 'Korean BBQ Food Truck', 'korean_restaurant', 'Herald Square, NY 10001', '2024-12-06 13:00:00'),
(125023, 40.7320, -73.9950, 'Indian Chaat Cart', 'indian_restaurant', 'Greenwich Village, NY 10012', '2024-12-06 11:00:00'),

-- Small Bistros & Casual Restaurants
(125023, 40.7195, -73.9935, 'Bleecker Street Deli', 'deli', 'New York, NY 10014', '2024-12-05 12:00:00'),
(125023, 40.7250, -73.9925, 'Eldridge Street Bistro', 'restaurant', '134 Eldridge St, New York, NY 10002', '2024-12-05 13:00:00'),

-- Food Festivals / Pop-up Events
(125023, 40.7570, -73.9855, 'NYC Street Food Festival', 'event_venue', 'Midtown, NY 10036', '2024-12-04 12:00:00'),
(125023, 40.7590, -73.9815, 'Union Square Food Pop-Up', 'event_venue', 'Union Square, NY 10003', '2024-12-04 11:00:00'),

-- Ice Cream & Snack Stops
(125023, 40.7290, -73.9955, 'Van Leeuwen Ice Cream', 'ice_cream_shop', 'East Village, NY 10009', '2024-12-03 10:30:00'),
(125023, 40.7420, -73.9885, 'Ample Hills Creamery', 'ice_cream_shop', 'Chelsea, NY 10011', '2024-12-03 11:30:00'),

-- Casual Drinks / Refreshments
(125023, 40.7410, -73.9880, 'Pressed Juicery', 'juice_shop', 'Flatiron, NY 10010', '2024-12-02 10:00:00'),
(125023, 40.7430, -73.9875, 'Joe & The Juice', 'juice_shop', 'Flatiron, NY 10010', '2024-12-02 11:00:00');

-- Check-in history for user 125024 (Family & Kids Focused)
-- This user's activities revolve around amusement parks, playgrounds, aquariums, zoos, and family-friendly restaurants.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Amusement & Adventure Centers
(125024, 40.5743, -73.9850, 'Coney Island Amusement Park', 'amusement_park', '1208 Surf Ave, Brooklyn, NY 11224', '2024-12-15 10:00:00'),
(125024, 40.7505, -73.9934, 'Luna Park', 'amusement_center', '1000 Surf Ave, Brooklyn, NY 11224', '2024-12-15 11:30:00'),
(125024, 40.7033, -73.9870, 'Kids Fun Zone', 'amusement_center', 'Brooklyn, NY 11201', '2024-12-14 10:00:00'),

-- Zoos & Aquariums
(125024, 40.7813, -73.9735, 'Central Park Zoo', 'zoo', 'East 64th St, New York, NY 10021', '2024-12-14 12:00:00'),
(125024, 40.8690, -73.8665, 'Bronx Zoo', 'zoo', '2300 Southern Blvd, Bronx, NY 10460', '2024-12-13 10:00:00'),
(125024, 40.6676, -73.9632, 'Prospect Park Zoo', 'zoo', '450 Flatbush Ave, Brooklyn, NY 11225', '2024-12-13 11:30:00'),
(125024, 40.5740, -73.9870, 'New York Aquarium', 'aquarium', '602 Surf Ave, Brooklyn, NY 11224', '2024-12-12 10:30:00'),

-- Playgrounds & Parks
(125024, 40.7851, -73.9683, 'Central Park Playground', 'playground', 'New York, NY 10024', '2024-12-12 09:00:00'),
(125024, 40.7030, -73.9900, 'Brooklyn Bridge Park Playground', 'playground', 'Brooklyn, NY 11201', '2024-12-11 09:30:00'),
(125024, 40.6700, -73.9700, 'Prospect Park Playground', 'playground', 'Brooklyn, NY 11225', '2024-12-11 10:00:00'),

-- Family-friendly Restaurants & Cafes
(125024, 40.7220, -73.9960, 'Eldridge Street Diner', 'diner', '134 Eldridge St, New York, NY 10002', '2024-12-10 12:00:00'),
(125024, 40.7190, -73.9930, 'Junior''s Restaurant', 'restaurant', '386 Flatbush Ave, Brooklyn, NY 11238', '2024-12-10 12:30:00'),
(125024, 40.7420, -73.9880, 'Serendipity 3', 'restaurant', '225 E 60th St, New York, NY 10022', '2024-12-09 11:30:00'),

-- Casual Markets & Snack Stops
(125024, 40.7420, -74.0048, 'Chelsea Market', 'market', '75 9th Ave, New York, NY 10011', '2024-12-09 10:00:00'),
(125024, 40.7441, -73.9933, 'Eataly NYC Flatiron', 'market', '200 5th Ave, New York, NY 10010', '2024-12-08 12:00:00'),

-- Light Leisure & Walking Areas
(125024, 40.7300, -73.9950, 'Washington Square Park', 'park', 'New York, NY 10012', '2024-12-08 09:00:00'),
(125024, 40.7829, -73.9654, 'Central Park', 'park', 'New York, NY 10024', '2024-12-07 09:30:00'),
(125024, 40.6676, -73.9632, 'Prospect Park', 'park', 'Brooklyn, NY 11225', '2024-12-07 10:30:00'),

-- Children’s Camps / Activity Centers
(125024, 40.7290, -73.9955, 'Little Gym NYC', 'childrens_camp', 'East Village, NY 10009', '2024-12-06 10:00:00'),
(125024, 40.7305, -73.9930, 'Tumbleweed Kids Camp', 'childrens_camp', 'Greenwich Village, NY 10012', '2024-12-06 11:30:00'),

-- More Playgrounds & Picnic Areas
(125024, 40.7310, -73.9970, 'Riverside Park Playground', 'playground', 'New York, NY 10024', '2024-12-05 09:30:00'),
(125024, 40.7680, -73.9810, 'Morningside Park Playground', 'playground', 'New York, NY 10027', '2024-12-05 10:30:00'),
(125024, 40.7280, -73.9950, 'Brooklyn Bridge Park', 'park', 'Brooklyn, NY 11201', '2024-12-04 09:00:00'),

-- Casual Cafes Near Family Spots
(125024, 40.7305, -73.9950, 'Think Coffee', 'coffee_shop', 'Greenwich Village, NY 10012', '2024-12-04 11:00:00'),
(125024, 40.7420, -73.9880, 'Bluestone Lane Cafe', 'cafe', 'Flatiron, NY 10010', '2024-12-03 10:00:00'),
(125024, 40.7410, -73.9885, 'Joe Coffee Company', 'coffee_shop', 'Flatiron, NY 10011', '2024-12-03 11:00:00');

-- Check-in history for user 125025 (Travel & Transit Enthusiast)
-- This user's activities revolve around airports, train stations, ferry terminals, bus stations, light rail stations, and car rentals.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Airports & Airstrips
(125025, 40.6413, -73.7781, 'John F. Kennedy International Airport', 'international_airport', 'Queens, NY 11430', '2024-12-15 08:00:00'),
(125025, 40.7769, -73.8740, 'LaGuardia Airport', 'airport', 'Queens, NY 11371', '2024-12-15 10:00:00'),
(125025, 40.6895, -74.1745, 'Newark Liberty International Airport', 'international_airport', 'Newark, NJ 07114', '2024-12-14 09:00:00'),

-- Train Stations
(125025, 40.7527, -73.9772, 'Grand Central Terminal', 'train_station', '89 E 42nd St, New York, NY 10017', '2024-12-14 11:00:00'),
(125025, 40.7506, -73.9935, 'Penn Station', 'train_station', 'New York, NY 10121', '2024-12-14 13:00:00'),

-- Bus & Transit Depots
(125025, 40.7569, -73.9903, 'Port Authority Bus Terminal', 'bus_station', '625 8th Ave, New York, NY 10018', '2024-12-13 10:00:00'),
(125025, 40.7565, -73.9900, 'MTA Bus Depot', 'transit_depot', 'New York, NY 10018', '2024-12-13 11:30:00'),

-- Ferry Terminals & Water Transit
(125025, 40.7003, -74.0124, 'Staten Island Ferry Terminal', 'ferry_terminal', '4 Whitehall St, New York, NY 10004', '2024-12-12 09:00:00'),
(125025, 40.7056, -74.0168, 'Battery Park Ferry Terminal', 'ferry_terminal', 'New York, NY 10004', '2024-12-12 10:30:00'),

-- Light Rail & Subway
(125025, 40.7012, -74.0131, 'World Trade Center Subway Station', 'subway_station', 'New York, NY 10007', '2024-12-11 08:30:00'),
(125025, 40.7500, -73.9940, '34th Street – Penn Station Subway', 'subway_station', 'New York, NY 10121', '2024-12-11 09:30:00'),
(125025, 40.7570, -73.9855, 'Times Square Subway Station', 'subway_station', 'New York, NY 10036', '2024-12-11 10:30:00'),

-- Car Rentals & Taxi Stands
(125025, 40.7580, -73.9855, 'Hertz Car Rental Midtown', 'car_rental', '150 W 45th St, New York, NY 10036', '2024-12-10 08:30:00'),
(125025, 40.7610, -73.9780, 'Avis Car Rental', 'car_rental', '635 5th Ave, New York, NY 10022', '2024-12-10 09:30:00'),
(125025, 40.7484, -73.9857, 'Taxi Stand – Empire State Building', 'taxi_stand', '20 W 34th St, New York, NY 10118', '2024-12-10 10:30:00'),

-- Transit-related Services
(125025, 40.7550, -73.9860, 'Travel Agency NYC', 'travel_agency', '123 W 45th St, New York, NY 10036', '2024-12-09 08:30:00'),
(125025, 40.7510, -73.9935, 'Amtrak Service Center', 'train_station', 'Penn Station, NY 10121', '2024-12-09 09:30:00'),

-- Casual Stops Near Transit
(125025, 40.7525, -73.9810, 'Starbucks – Grand Central', 'coffee_shop', '89 E 42nd St, New York, NY 10017', '2024-12-08 09:00:00'),
(125025, 40.7580, -73.9850, 'Pret A Manger', 'cafe', 'Midtown, NY 10036', '2024-12-08 10:00:00'),

-- Observation / Leisure Spots Near Hubs
(125025, 40.7484, -73.9857, 'Empire State Building Observation Deck', 'observation_deck', '20 W 34th St, New York, NY 10118', '2024-12-07 08:30:00'),
(125025, 40.7061, -74.0086, 'Battery Park', 'park', 'New York, NY 10004', '2024-12-07 09:30:00'),

-- Additional Transit & Car Services
(125025, 40.7560, -73.9900, 'Enterprise Car Rental', 'car_rental', '8th Ave, New York, NY 10018', '2024-12-06 08:30:00'),
(125025, 40.7555, -73.9875, 'NYC Transit Information Center', 'tourist_information_center', 'Midtown, NY 10036', '2024-12-06 09:30:00'),
(125025, 40.7515, -73.9775, 'Grand Central Post Office', 'post_office', 'New York, NY 10017', '2024-12-06 10:30:00'),
(125025, 40.7500, -73.9945, 'Penn Station Parking', 'parking', 'New York, NY 10121', '2024-12-05 08:30:00');

-- Check-in history for user 125026 (Arts & Performance Lover)
-- This user's activities revolve around theaters, opera houses, concert halls, auditoriums, dance halls, and comedy clubs, with some diverse leisure spots.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Theaters & Opera Houses
(125026, 40.7632, -73.9836, 'Broadway Theater', 'performing_arts_theater', '1681 Broadway, New York, NY 10019', '2024-12-15 14:00:00'),
(125026, 40.7590, -73.9845, 'Lyric Opera House', 'opera_house', '20 W 42nd St, New York, NY 10036', '2024-12-15 19:00:00'),
(125026, 40.7616, -73.9795, 'Carnegie Hall', 'concert_hall', '881 7th Ave, New York, NY 10019', '2024-12-14 20:00:00'),
(125026, 40.7480, -73.9875, 'Empire Dance Studio', 'dance_hall', '23rd St, New York, NY 10010', '2024-12-14 17:00:00'),
(125026, 40.7300, -73.9970, 'Comedy Cellar', 'comedy_club', '117 MacDougal St, New York, NY 10012', '2024-12-13 20:30:00'),

-- Auditoriums & Cultural Centers
(125026, 40.7295, -73.9975, 'NYU Skirball Center', 'auditorium', '566 LaGuardia Pl, New York, NY 10012', '2024-12-13 14:00:00'),
(125026, 40.7485, -73.9850, 'Times Square Arts Center', 'cultural_center', 'New York, NY 10036', '2024-12-12 15:00:00'),

-- Art Galleries & Museums (light diversity)
(125026, 40.7490, -73.9950, 'Chelsea Art Gallery', 'art_gallery', 'Chelsea, NY 10011', '2024-12-12 11:00:00'),
(125026, 40.7614, -73.9776, 'Modern Art Studio', 'art_studio', 'Midtown, NY 10019', '2024-12-11 12:00:00'),

-- Parks & Leisure Walks
(125026, 40.7851, -73.9683, 'Central Park', 'park', 'New York, NY 10024', '2024-12-11 10:00:00'),
(125026, 40.7300, -73.9950, 'Washington Square Park', 'park', 'New York, NY 10012', '2024-12-10 09:30:00'),

-- Cafes & Casual Stops Near Venues
(125026, 40.7420, -73.9870, 'Bluestone Lane Cafe', 'cafe', 'Flatiron, NY 10010', '2024-12-10 11:00:00'),
(125026, 40.7295, -73.9965, 'Think Coffee', 'coffee_shop', 'Greenwich Village, NY 10012', '2024-12-09 10:30:00'),
(125026, 40.7580, -73.9855, 'Pret A Manger', 'cafe', 'Midtown, NY 10036', '2024-12-09 09:30:00'),

-- Dance & Rehearsal Spaces
(125026, 40.7480, -73.9870, 'Broadway Dance Rehearsal Studio', 'dance_hall', 'Flatiron, NY 10010', '2024-12-08 14:00:00'),
(125026, 40.7610, -73.9800, 'Carnegie Hall Rehearsal Room', 'concert_hall', '881 7th Ave, New York, NY 10019', '2024-12-08 16:00:00'),

-- Evening Performances & Comedy
(125026, 40.7305, -73.9970, 'Upstate Comedy Club', 'comedy_club', 'East Village, NY 10012', '2024-12-07 19:30:00'),
(125026, 40.7590, -73.9845, 'Lincoln Center Theater', 'performing_arts_theater', '10 Lincoln Center Plaza, NY 10023', '2024-12-07 20:00:00'),

-- Cultural Events / Small Venues
(125026, 40.7484, -73.9857, 'Flatiron Cultural Center', 'cultural_center', '23rd St, New York, NY 10010', '2024-12-06 13:00:00'),
(125026, 40.7290, -73.9960, 'Village Arts Hall', 'auditorium', 'Greenwich Village, NY 10012', '2024-12-06 14:30:00'),

-- Specialty Coffee & Light Bites Near Venues
(125026, 40.7410, -73.9880, 'Joe Coffee Company', 'coffee_shop', 'Flatiron, NY 10011', '2024-12-05 10:00:00'),
(125026, 40.7425, -73.9875, 'Bluestone Lane', 'cafe', 'Flatiron, NY 10010', '2024-12-05 11:00:00'),

-- Small Galleries & Art Studios
(125026, 40.7500, -73.9940, 'Chelsea Fine Arts', 'art_gallery', 'Chelsea, NY 10011', '2024-12-04 11:00:00'),
(125026, 40.7615, -73.9785, 'Midtown Art Studio', 'art_studio', 'NY 10019', '2024-12-04 12:00:00'),

-- Light Parks & Outdoor Leisure
(125026, 40.7677, -73.9718, 'Riverside Park', 'park', 'Upper West Side, NY 10024', '2024-12-03 09:00:00'),
(125026, 40.7700, -73.9740, 'Morningside Park', 'park', 'New York, NY 10027', '2024-12-03 10:00:00');

-- Check-in history for user 125027 (Music & Vinyl Collector)
-- This user's activities revolve around record stores, music venues, rehearsal studios, small live music bars, and music-themed cafes.

INSERT INTO new_user_visits (user_id, lat, long, name, place_type, address, created_at) VALUES
-- Record Stores
(125027, 40.7240, -73.9980, 'Rough Trade NYC', 'record_store', '64 N 9th St, Brooklyn, NY 11249', '2024-12-15 11:00:00'),
(125027, 40.7285, -73.9980, 'Other Music Record Shop', 'record_store', 'Greenwich Village, NY 10012', '2024-12-15 12:30:00'),
(125027, 40.7410, -73.9880, 'Rebel Rebel Records', 'record_store', 'Flatiron, NY 10010', '2024-12-14 10:30:00'),
(125027, 40.7300, -73.9950, 'Turntable Vinyl', 'record_store', 'East Village, NY 10003', '2024-12-14 12:00:00'),

-- Music Venues & Small Bars (daytime performances)
(125027, 40.7290, -73.9970, 'Village Vanguard', 'music_venue', '178 7th Ave S, New York, NY 10014', '2024-12-13 14:00:00'),
(125027, 40.7225, -73.9985, 'Smalls Jazz Club', 'music_venue', '183 W 10th St, New York, NY 10014', '2024-12-13 16:00:00'),
(125027, 40.7260, -73.9970, 'Rockwood Music Hall', 'music_venue', '196 Allen St, New York, NY 10002', '2024-12-12 13:30:00'),
(125027, 40.7305, -73.9950, 'Fat Cat', 'music_venue', '75 Christopher St, New York, NY 10014', '2024-12-12 15:00:00'),

-- Rehearsal Studios
(125027, 40.7420, -73.9870, 'Midtown Music Rehearsal Studio', 'concert_hall', 'Flatiron, NY 10010', '2024-12-11 09:00:00'),
(125027, 40.7590, -73.9845, 'Lincoln Center Rehearsal Room', 'concert_hall', 'Lincoln Center, NY 10023', '2024-12-11 10:30:00'),

-- Music-themed Cafes & Coffee Shops
(125027, 40.7295, -73.9960, 'Café Wha?', 'cafe', 'Greenwich Village, NY 10012', '2024-12-10 11:00:00'),
(125027, 40.7310, -73.9950, 'Think Coffee', 'coffee_shop', 'Greenwich Village, NY 10012', '2024-12-10 12:00:00'),
(125027, 40.7425, -73.9875, 'Bluestone Lane', 'cafe', 'Flatiron, NY 10010', '2024-12-09 10:30:00'),

-- Parks & Outdoor Stops Near Music Areas
(125027, 40.7300, -73.9970, 'Washington Square Park', 'park', 'New York, NY 10012', '2024-12-09 09:00:00'),
(125027, 40.7410, -73.9880, 'Madison Square Park', 'park', 'New York, NY 10010', '2024-12-08 09:30:00'),

-- Vinyl & Music Collectibles
(125027, 40.7245, -73.9985, 'Academy Records', 'record_store', 'Brooklyn, NY 11222', '2024-12-08 11:00:00'),
(125027, 40.7280, -73.9970, 'A-1 Records', 'record_store', 'Greenwich Village, NY 10012', '2024-12-07 12:00:00'),

-- Small Gigs / Daytime Live Music
(125027, 40.7305, -73.9950, 'Caffe Vivaldi', 'music_venue', '32 Jones St, New York, NY 10014', '2024-12-07 14:00:00'),
(125027, 40.7275, -73.9955, 'Arlene’s Grocery (Daytime Session)', 'music_venue', '95 Stanton St, New York, NY 10002', '2024-12-06 15:00:00'),

-- Specialty Shops / Accessories
(125027, 40.7415, -73.9885, 'Vinyl Me, Please Store', 'record_store', 'Flatiron, NY 10010', '2024-12-06 10:30:00'),
(125027, 40.7300, -73.9960, 'Music Lovers Supply', 'record_store', 'East Village, NY 10003', '2024-12-05 11:00:00'),

-- Additional Parks & Leisure Walks
(125027, 40.7320, -73.9980, 'Tompkins Square Park', 'park', 'New York, NY 10009', '2024-12-05 09:30:00'),
(125027, 40.7290, -73.9955, 'Hudson River Park', 'park', 'New York, NY 10014', '2024-12-04 10:00:00'),

-- Light Food Stops
(125027, 40.7420, -73.9870, 'Gregorys Coffee', 'coffee_shop', 'Flatiron, NY 10010', '2024-12-04 09:00:00');
