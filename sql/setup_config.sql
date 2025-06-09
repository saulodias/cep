-- Drop if exists
DROP TEXT SEARCH CONFIGURATION IF EXISTS public.address_pt CASCADE;
DROP TEXT SEARCH DICTIONARY IF EXISTS public.address_pt_dict CASCADE;

CREATE EXTENSION IF NOT EXISTS unaccent;

-- Create the configuration
CREATE TEXT SEARCH CONFIGURATION public.address_pt (COPY = portuguese);

-- Create the dictionary
CREATE TEXT SEARCH DICTIONARY public.address_pt_dict (
    TEMPLATE = synonym,
    SYNONYMS = address_pt
);

-- Add the dictionary to handle all relevant token types
ALTER TEXT SEARCH CONFIGURATION public.address_pt 
    ALTER MAPPING FOR asciiword, asciihword, word, hword, numword, numhword, hword_asciipart, hword_part, hword_numpart
    WITH address_pt_dict, portuguese_stem;

-- Verify
SELECT cfgname 
FROM pg_ts_config 
WHERE cfgname = 'address_pt';
