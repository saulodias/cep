-- Create normalization table for day numbers
CREATE TABLE IF NOT EXISTS day_numbers (
    number text PRIMARY KEY,
    word_form text NOT NULL
);

-- Insert day number mappings (cardinal numbers)
INSERT INTO day_numbers (number, word_form) VALUES
    ('1', 'primeiro'),
    ('2', 'dois'),
    ('3', 'três'),
    ('4', 'quatro'),
    ('5', 'cinco'),
    ('6', 'seis'),
    ('7', 'sete'),
    ('8', 'oito'),
    ('9', 'nove'),
    ('10', 'dez'),
    ('11', 'onze'),
    ('12', 'doze'),
    ('13', 'treze'),
    ('14', 'quatorze'),
    ('15', 'quinze'),
    ('16', 'dezesseis'),
    ('17', 'dezessete'),
    ('18', 'dezoito'),
    ('19', 'dezenove'),
    ('20', 'vinte'),
    ('21', 'vinte e um'),
    ('22', 'vinte e dois'),
    ('23', 'vinte e três'),
    ('24', 'vinte e quatro'),
    ('25', 'vinte e cinco'),
    ('26', 'vinte e seis'),
    ('27', 'vinte e sete'),
    ('28', 'vinte e oito'),
    ('29', 'vinte e nove'),
    ('30', 'trinta'),
    ('31', 'trinta e um'),
    -- Ordinal forms (feminine)
    ('1ª', 'primeira'),
    ('2ª', 'segunda'),
    ('3ª', 'terceira'),
    ('4ª', 'quarta'),
    ('5ª', 'quinta'),
    ('6ª', 'sexta'),
    ('7ª', 'sétima'),
    ('8ª', 'oitava'),
    ('9ª', 'nona'),
    ('10ª', 'décima'),
    ('11ª', 'décima primeira'),
    ('12ª', 'décima segunda'),
    ('13ª', 'décima terceira'),
    ('14ª', 'décima quarta'),
    ('15ª', 'décima quinta'),
    ('16ª', 'décima sexta'),
    ('17ª', 'décima sétima'),
    ('18ª', 'décima oitava'),
    ('19ª', 'décima nona'),
    ('20ª', 'vigésima'),
    ('21ª', 'vigésima primeira'),
    ('22ª', 'vigésima segunda'),
    ('23ª', 'vigésima terceira'),
    ('24ª', 'vigésima quarta'),
    ('25ª', 'vigésima quinta'),
    ('26ª', 'vigésima sexta'),
    ('27ª', 'vigésima sétima'),
    ('28ª', 'vigésima oitava'),
    ('29ª', 'vigésima nona'),
    ('30ª', 'trigésima'),
    ('31ª', 'trigésima primeira'),
    -- Ordinal forms (masculine)
    ('1º', 'primeiro'),
    ('2º', 'segundo'),
    ('3º', 'terceiro'),
    ('4º', 'quarto'),
    ('5º', 'quinto'),
    ('6º', 'sexto'),
    ('7º', 'sétimo'),
    ('8º', 'oitavo'),
    ('9º', 'nono'),
    ('10º', 'décimo'),
    ('11º', 'décimo primeiro'),
    ('12º', 'décimo segundo'),
    ('13º', 'décimo terceiro'),
    ('14º', 'décimo quarto'),
    ('15º', 'décimo quinto'),
    ('16º', 'décimo sexto'),
    ('17º', 'décimo sétimo'),
    ('18º', 'décimo oitavo'),
    ('19º', 'décimo nono'),
    ('20º', 'vigésimo'),
    ('21º', 'vigésimo primeiro'),
    ('22º', 'vigésimo segundo'),
    ('23º', 'vigésimo terceiro'),
    ('24º', 'vigésimo quarto'),
    ('25º', 'vigésimo quinto'),
    ('26º', 'vigésimo sexto'),
    ('27º', 'vigésimo sétimo'),
    ('28º', 'vigésimo oitavo'),
    ('29º', 'vigésimo nono'),
    ('30º', 'trigésimo'),
    ('31º', 'trigésimo primeiro'),
    -- Alternative ordinal forms (simplified)
    ('1a', 'primeira'),
    ('2a', 'segunda'),
    ('3a', 'terceira'),
    ('4a', 'quarta'),
    ('5a', 'quinta'),
    ('6a', 'sexta'),
    ('7a', 'sétima'),
    ('8a', 'oitava'),
    ('9a', 'nona'),
    ('10a', 'décima'),
    ('1o', 'primeiro'),
    ('2o', 'segundo'),
    ('3o', 'terceiro'),
    ('4o', 'quarto'),
    ('5o', 'quinto'),
    ('6o', 'sexto'),
    ('7o', 'sétimo'),
    ('8o', 'oitavo'),
    ('9o', 'nono'),
    ('10o', 'décimo')
ON CONFLICT (number) DO UPDATE SET word_form = EXCLUDED.word_form;

-- Normalize any numbers in address text (not just with 'de')
CREATE OR REPLACE FUNCTION normalize_address_numbers(input_text text)
RETURNS text AS $$
DECLARE
    result text;
    matches text[];
    match_text text;
    replacement text;
BEGIN
    result := lower(trim(input_text));
    
    -- Find all number patterns and replace them
    FOR match_text IN 
        SELECT unnest(regexp_split_to_array(result, '\s+'))
    LOOP
        -- Check if this word matches our number pattern
        IF match_text ~ '^\d+[ªºao]?$' THEN
            -- Look up replacement
            SELECT word_form INTO replacement 
            FROM day_numbers 
            WHERE number = match_text;
            
            IF replacement IS NOT NULL THEN
                result := replace(result, match_text, replacement);
            END IF;
        END IF;
    END LOOP;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Test the normalization
SELECT normalize_address_numbers('28 de setembro') as test1;
SELECT normalize_address_numbers('vinte e oito de setembro') as test2;  
SELECT normalize_address_numbers('rua 28') as test3;  -- Now normalizes!
SELECT normalize_address_numbers('avenida 1ª') as test4;  -- Ordinals work!
SELECT normalize_address_numbers('boulevard 28') as test5;  -- Any context!
SELECT normalize_address_numbers('1o de marco') as test6;
SELECT normalize_address_numbers('1º de marco') as test7;
