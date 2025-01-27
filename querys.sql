CREATE TABLE alembic_version (
        version_num VARCHAR(32) NOT NULL, 
        CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

CREATE TABLE sqlite_sequence(name,seq);

CREATE TABLE users (
        id INTEGER NOT NULL,
        username VARCHAR(120) NOT NULL,
        email VARCHAR(120) NOT NULL,
        pw_hash VARCHAR(120) NOT NULL,
        PRIMARY KEY (id),
        UNIQUE (email)
);

CREATE TABLE species (
        id INTEGER NOT NULL,
        name VARCHAR(100) NOT NULL,
        PRIMARY KEY (id),
        UNIQUE (name)
);

CREATE TABLE breeds (
        id INTEGER NOT NULL,
        species_id INTEGER NOT NULL,
        name VARCHAR(100) NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(species_id) REFERENCES species (id)
);

CREATE TABLE pets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    pet_profile_photo TEXT,
    name VARCHAR(80) NOT NULL,
    birth_date DATE,
    adoption_date DATE,
    sex TEXT NOT NULL CHECK (sex IN ('M', 'F')),
    species_id INTEGER NOT NULL,
    breed_id INTEGER,
    sterilized BOOLEAN NOT NULL DEFAULT 0,
    microchip_number VARCHAR(50),
    insurance_company VARCHAR(100),
    insurance_number VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (species_id) REFERENCES species(id),
    FOREIGN KEY (breed_id) REFERENCES breeds(id)
);

CREATE TABLE photos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_id INTERGER NOT NULL,
    image_url TEXT NOT NULL,
    title VARCHAR(100),
    date_uploaded DATE,
    FOREIGN KEY (pet_id) REFERENCES pets(id)
);

CREATE TABLE logs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_id INTEGER NOT NULL,
    title VARCHAR(150),
    date_uploaded DATE NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY(pet_id) REFERENCES pets(id)
);