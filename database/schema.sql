-- Car Trends Analysis Tool Database Schema
-- PostgreSQL 15+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create database if not exists (run this manually)
-- CREATE DATABASE car_trends;

-- Listings table - stores individual car listings from all platforms
CREATE TABLE IF NOT EXISTS listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('facebook', 'craigslist', 'mercadolibre')),
    external_id VARCHAR(100) NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    make VARCHAR(50),
    model VARCHAR(50),
    year INTEGER CHECK (year >= 1900 AND year <= EXTRACT(YEAR FROM NOW()) + 1),
    price DECIMAL(12,2) CHECK (price >= 0),
    currency VARCHAR(3) DEFAULT 'MXN',
    condition VARCHAR(20) CHECK (condition IN ('new', 'used', 'certified', 'salvage', 'other')),
    mileage INTEGER CHECK (mileage >= 0),
    location VARCHAR(100),
    url TEXT NOT NULL,
    images TEXT[], -- Array of image URLs
    
    -- Engagement metrics
    views INTEGER DEFAULT 0 CHECK (views >= 0),
    likes INTEGER DEFAULT 0 CHECK (likes >= 0),
    comments INTEGER DEFAULT 0 CHECK (comments >= 0),
    saves INTEGER DEFAULT 0 CHECK (saves >= 0),
    shares INTEGER DEFAULT 0 CHECK (shares >= 0),
    
    -- Metadata
    posted_date TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    is_duplicate BOOLEAN DEFAULT FALSE,
    
    -- Constraints
    UNIQUE(platform, external_id),
    CONSTRAINT valid_price CHECK (price IS NULL OR price > 0),
    CONSTRAINT valid_year CHECK (year IS NULL OR (year >= 1900 AND year <= EXTRACT(YEAR FROM NOW()) + 1))
);

-- Trends table - aggregated daily trends by make/model
CREATE TABLE IF NOT EXISTS trends (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    
    -- Aggregated metrics
    total_listings INTEGER DEFAULT 0 CHECK (total_listings >= 0),
    avg_price DECIMAL(12,2) CHECK (avg_price >= 0),
    min_price DECIMAL(12,2) CHECK (min_price >= 0),
    max_price DECIMAL(12,2) CHECK (max_price >= 0),
    total_views INTEGER DEFAULT 0 CHECK (total_views >= 0),
    total_likes INTEGER DEFAULT 0 CHECK (total_likes >= 0),
    total_comments INTEGER DEFAULT 0 CHECK (total_comments >= 0),
    total_saves INTEGER DEFAULT 0 CHECK (total_saves >= 0),
    total_shares INTEGER DEFAULT 0 CHECK (total_shares >= 0),
    engagement_score DECIMAL(10,2) DEFAULT 0,
    
    -- Calculated metrics
    price_change_pct DECIMAL(5,2),
    listing_change_pct DECIMAL(5,2),
    engagement_change_pct DECIMAL(5,2),
    
    -- Constraints
    UNIQUE(make, model, date),
    CONSTRAINT valid_avg_price CHECK (avg_price IS NULL OR avg_price > 0),
    CONSTRAINT valid_min_price CHECK (min_price IS NULL OR min_price > 0),
    CONSTRAINT valid_max_price CHECK (max_price IS NULL OR max_price > 0),
    CONSTRAINT price_range CHECK (min_price IS NULL OR max_price IS NULL OR min_price <= max_price)
);

-- Scraping sessions table - tracks scraping operations
CREATE TABLE IF NOT EXISTS scraping_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('facebook', 'craigslist', 'mercadolibre')),
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),
    listings_found INTEGER DEFAULT 0 CHECK (listings_found >= 0),
    listings_processed INTEGER DEFAULT 0 CHECK (listings_processed >= 0),
    listings_new INTEGER DEFAULT 0 CHECK (listings_new >= 0),
    listings_updated INTEGER DEFAULT 0 CHECK (listings_updated >= 0),
    errors TEXT[],
    execution_time_seconds INTEGER CHECK (execution_time_seconds >= 0),
    
    -- Constraints
    CONSTRAINT valid_completion CHECK (
        (status = 'running' AND completed_at IS NULL) OR
        (status IN ('completed', 'failed', 'cancelled') AND completed_at IS NOT NULL)
    ),
    CONSTRAINT valid_processed CHECK (listings_processed <= listings_found)
);

-- Users table - for authentication
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- User sessions table - for JWT token management
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Constraints
    CONSTRAINT valid_expiry CHECK (expires_at > created_at)
);

-- Car models normalization table - for consistent make/model names
CREATE TABLE IF NOT EXISTS car_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    normalized_make VARCHAR(50) NOT NULL,
    normalized_model VARCHAR(50) NOT NULL,
    category VARCHAR(20) CHECK (category IN ('sedan', 'suv', 'truck', 'coupe', 'convertible', 'hatchback', 'wagon', 'other')),
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(make, model)
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_listings_platform_scraped ON listings(platform, scraped_at);
CREATE INDEX IF NOT EXISTS idx_listings_make_model ON listings(make, model);
CREATE INDEX IF NOT EXISTS idx_listings_price ON listings(price);
CREATE INDEX IF NOT EXISTS idx_listings_posted_date ON listings(posted_date);
CREATE INDEX IF NOT EXISTS idx_listings_active ON listings(is_active);
CREATE INDEX IF NOT EXISTS idx_listings_engagement ON listings(views, likes, comments);

CREATE INDEX IF NOT EXISTS idx_trends_make_model_date ON trends(make, model, date);
CREATE INDEX IF NOT EXISTS idx_trends_date ON trends(date);
CREATE INDEX IF NOT EXISTS idx_trends_engagement ON trends(engagement_score);

CREATE INDEX IF NOT EXISTS idx_scraping_sessions_platform ON scraping_sessions(platform);
CREATE INDEX IF NOT EXISTS idx_scraping_sessions_status ON scraping_sessions(status);
CREATE INDEX IF NOT EXISTS idx_scraping_sessions_started ON scraping_sessions(started_at);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(token_hash);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions(expires_at);

CREATE INDEX IF NOT EXISTS idx_car_models_normalized ON car_models(normalized_make, normalized_model);

-- Views for common queries

-- View for top cars by engagement
CREATE OR REPLACE VIEW top_cars_by_engagement AS
SELECT 
    make,
    model,
    COUNT(*) as total_listings,
    AVG(price) as avg_price,
    SUM(views) as total_views,
    SUM(likes) as total_likes,
    SUM(comments) as total_comments,
    SUM(saves) as total_saves,
    SUM(shares) as total_shares,
    (SUM(views) * 1.0 + SUM(likes) * 3.0 + SUM(comments) * 5.0 + SUM(saves) * 2.0 + SUM(shares) * 4.0) as engagement_score
FROM listings 
WHERE is_active = TRUE 
    AND scraped_at >= CURRENT_DATE - INTERVAL '30 days'
    AND make IS NOT NULL 
    AND model IS NOT NULL
GROUP BY make, model
HAVING COUNT(*) >= 3  -- Minimum 3 listings to be considered
ORDER BY engagement_score DESC;

-- View for recent trends
CREATE OR REPLACE VIEW recent_trends AS
SELECT 
    t.make,
    t.model,
    t.date,
    t.total_listings,
    t.avg_price,
    t.engagement_score,
    t.price_change_pct,
    t.listing_change_pct,
    t.engagement_change_pct,
    LAG(t.avg_price) OVER (PARTITION BY t.make, t.model ORDER BY t.date) as prev_avg_price,
    LAG(t.total_listings) OVER (PARTITION BY t.make, t.model ORDER BY t.date) as prev_total_listings,
    LAG(t.engagement_score) OVER (PARTITION BY t.make, t.model ORDER BY t.date) as prev_engagement_score
FROM trends t
WHERE t.date >= CURRENT_DATE - INTERVAL '90 days'
ORDER BY t.make, t.model, t.date;

-- Functions for data processing

-- Function to calculate engagement score
CREATE OR REPLACE FUNCTION calculate_engagement_score(
    views INTEGER,
    likes INTEGER,
    comments INTEGER,
    saves INTEGER,
    shares INTEGER
) RETURNS DECIMAL AS $$
BEGIN
    RETURN COALESCE(views, 0) * 1.0 + 
           COALESCE(likes, 0) * 3.0 + 
           COALESCE(comments, 0) * 5.0 + 
           COALESCE(saves, 0) * 2.0 + 
           COALESCE(shares, 0) * 4.0;
END;
$$ LANGUAGE plpgsql;

-- Function to normalize car make/model names
CREATE OR REPLACE FUNCTION normalize_car_name(input_name TEXT) RETURNS TEXT AS $$
BEGIN
    -- Convert to lowercase and trim
    input_name := LOWER(TRIM(input_name));
    
    -- Common normalizations
    input_name := REPLACE(input_name, 'chevrolet', 'chevy');
    input_name := REPLACE(input_name, 'mercedes-benz', 'mercedes');
    input_name := REPLACE(input_name, 'bmw', 'bmw');
    input_name := REPLACE(input_name, 'volkswagen', 'vw');
    input_name := REPLACE(input_name, 'toyota', 'toyota');
    input_name := REPLACE(input_name, 'honda', 'honda');
    input_name := REPLACE(input_name, 'nissan', 'nissan');
    input_name := REPLACE(input_name, 'ford', 'ford');
    input_name := REPLACE(input_name, 'hyundai', 'hyundai');
    input_name := REPLACE(input_name, 'kia', 'kia');
    
    RETURN input_name;
END;
$$ LANGUAGE plpgsql;

-- Triggers for automatic data processing

-- Trigger to update engagement score when listing is updated
CREATE OR REPLACE FUNCTION update_listing_engagement_score() RETURNS TRIGGER AS $$
BEGIN
    -- This trigger can be used to automatically calculate engagement scores
    -- when listing data is updated
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically create trends when listings are inserted/updated
CREATE OR REPLACE FUNCTION update_daily_trends() RETURNS TRIGGER AS $$
DECLARE
    trend_date DATE;
BEGIN
    -- Only process if make and model are present
    IF NEW.make IS NOT NULL AND NEW.model IS NOT NULL THEN
        trend_date := CURRENT_DATE;
        
        -- Insert or update trend for today
        INSERT INTO trends (make, model, date, total_listings, avg_price, total_views, total_likes, total_comments, total_saves, total_shares, engagement_score)
        SELECT 
            NEW.make,
            NEW.model,
            trend_date,
            COUNT(*),
            AVG(price),
            SUM(views),
            SUM(likes),
            SUM(comments),
            SUM(saves),
            SUM(shares),
            SUM(calculate_engagement_score(views, likes, comments, saves, shares))
        FROM listings 
        WHERE make = NEW.make 
            AND model = NEW.model 
            AND DATE(scraped_at) = trend_date
            AND is_active = TRUE
        ON CONFLICT (make, model, date) 
        DO UPDATE SET
            total_listings = EXCLUDED.total_listings,
            avg_price = EXCLUDED.avg_price,
            total_views = EXCLUDED.total_views,
            total_likes = EXCLUDED.total_likes,
            total_comments = EXCLUDED.total_comments,
            total_saves = EXCLUDED.total_saves,
            total_shares = EXCLUDED.total_shares,
            engagement_score = EXCLUDED.engagement_score;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers
DROP TRIGGER IF EXISTS trigger_update_daily_trends ON listings;
CREATE TRIGGER trigger_update_daily_trends
    AFTER INSERT OR UPDATE ON listings
    FOR EACH ROW
    EXECUTE FUNCTION update_daily_trends();

-- Insert sample car models for normalization
INSERT INTO car_models (make, model, normalized_make, normalized_model, category) VALUES
('Toyota', 'Camry', 'toyota', 'camry', 'sedan'),
('Toyota', 'Corolla', 'toyota', 'corolla', 'sedan'),
('Toyota', 'RAV4', 'toyota', 'rav4', 'suv'),
('Honda', 'Civic', 'honda', 'civic', 'sedan'),
('Honda', 'Accord', 'honda', 'accord', 'sedan'),
('Honda', 'CR-V', 'honda', 'cr-v', 'suv'),
('Nissan', 'Sentra', 'nissan', 'sentra', 'sedan'),
('Nissan', 'Altima', 'nissan', 'altima', 'sedan'),
('Nissan', 'Rogue', 'nissan', 'rogue', 'suv'),
('Ford', 'F-150', 'ford', 'f-150', 'truck'),
('Ford', 'Focus', 'ford', 'focus', 'sedan'),
('Ford', 'Escape', 'ford', 'escape', 'suv'),
('Chevrolet', 'Silverado', 'chevy', 'silverado', 'truck'),
('Chevrolet', 'Malibu', 'chevy', 'malibu', 'sedan'),
('Chevrolet', 'Equinox', 'chevy', 'equinox', 'suv'),
('BMW', '3 Series', 'bmw', '3-series', 'sedan'),
('BMW', 'X3', 'bmw', 'x3', 'suv'),
('Mercedes-Benz', 'C-Class', 'mercedes', 'c-class', 'sedan'),
('Mercedes-Benz', 'GLC', 'mercedes', 'glc', 'suv'),
('Audi', 'A4', 'audi', 'a4', 'sedan'),
('Audi', 'Q5', 'audi', 'q5', 'suv'),
('Volkswagen', 'Jetta', 'vw', 'jetta', 'sedan'),
('Volkswagen', 'Tiguan', 'vw', 'tiguan', 'suv'),
('Hyundai', 'Elantra', 'hyundai', 'elantra', 'sedan'),
('Hyundai', 'Tucson', 'hyundai', 'tucson', 'suv'),
('Kia', 'Forte', 'kia', 'forte', 'sedan'),
('Kia', 'Sportage', 'kia', 'sportage', 'suv')
ON CONFLICT (make, model) DO NOTHING;

-- Create default admin user (password: admin123 - change this!)
INSERT INTO users (username, email, hashed_password, full_name, is_superuser) VALUES
('admin', 'admin@cartrends.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8K5K5K.', 'System Administrator', TRUE)
ON CONFLICT (username) DO NOTHING;
