```bash
CREATE DATABASE digiboxx;

USE digiboxx;

CREATE TABLE auth (
    user_id CHAR(36),
    email_id VARCHAR(255),
    password VARCHAR(72),
    PRIMARY KEY (user_id, email_id)
);

COMMIT;
```