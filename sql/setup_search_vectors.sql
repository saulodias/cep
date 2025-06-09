-- Setup search vectors for the ceps_search table

-- Use existing address_pt configuration from setup_config.sql
-- No need to recreate it here

-- Create function to create search vector
CREATE OR REPLACE FUNCTION create_search_vector(logradouro text, complemento text, bairro text, cidade text, uf text)
RETURNS tsvector AS $$
DECLARE
    original_address text;
    normalized_address text;
BEGIN
    -- Create original address string
    original_address := COALESCE(logradouro, '') || ' ' ||
                        COALESCE(complemento, '') || ' ' ||
                        COALESCE(bairro, '') || ' ' ||
                        COALESCE(cidade, '') || ' ' ||
                        COALESCE(uf, '');
    
    -- Normalize the address
    normalized_address := normalize_address(original_address);
    
    -- Create tsvector with both versions
    RETURN setweight(to_tsvector('address_pt', normalized_address), 'A') ||
           setweight(to_tsvector('address_pt', COALESCE(cidade, '')), 'B') ||
           setweight(to_tsvector('address_pt', COALESCE(uf, '')), 'C');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Create trigger function to update search vectors
CREATE OR REPLACE FUNCTION trigger_update_search_vector()
RETURNS trigger AS $$
BEGIN
    NEW.search_vector := create_search_vector(
        NEW.logradouro, 
        NEW.complemento, 
        NEW.bairro, 
        NEW.cidade, 
        NEW.uf
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger
DROP TRIGGER IF EXISTS trig_update_search_vector ON ceps_search;
CREATE TRIGGER trig_update_search_vector
    BEFORE INSERT OR UPDATE OF logradouro, complemento, bairro, cidade, uf
    ON ceps_search
    FOR EACH ROW
    EXECUTE FUNCTION trigger_update_search_vector();

-- Create function to update search vectors
CREATE OR REPLACE FUNCTION update_search_vectors()
RETURNS void AS $$
BEGIN
    -- Update existing records
    UPDATE ceps_search 
    SET search_vector = create_search_vector(
        logradouro, 
        complemento, 
        bairro, 
        cidade, 
        uf
    )
    WHERE search_vector IS NULL;
END;
$$ LANGUAGE plpgsql;

-- Create function to update all search vectors with progress tracking
CREATE OR REPLACE FUNCTION update_all_search_vectors()
RETURNS void AS $$
DECLARE
    total_records integer;
    current_record integer := 0;
    batch_size integer := 100;
BEGIN
    -- Get total number of records
    SELECT COUNT(*) INTO total_records FROM ceps_search;
    
    -- Update with progress tracking
    FOR current_record IN 1..total_records BY batch_size LOOP
        UPDATE ceps_search 
        SET search_vector = create_search_vector(
            logradouro, 
            complemento, 
            bairro, 
            cidade, 
            uf
        )
        WHERE id >= current_record AND id < current_record + batch_size;
        
        RAISE NOTICE 'Progress: %%%', round((current_record * 100.0) / total_records, 1);
    END LOOP;
    
    -- Update remaining records
    UPDATE ceps_search 
    SET search_vector = create_search_vector(
        logradouro, 
        complemento, 
        bairro, 
        cidade, 
        uf
    )
    WHERE id >= current_record;
END;
$$ LANGUAGE plpgsql;

-- Note: To update search vectors manually, run:
-- SELECT update_all_search_vectors();
