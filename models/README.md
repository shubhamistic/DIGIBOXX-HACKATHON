```bash
CREATE DATABASE digiboxx;
```

```bash
USE digiboxx;
```

```bash
CREATE TABLE auth (
    user_id CHAR(36),
    email_id VARCHAR(255),
    password VARCHAR(72),
    PRIMARY KEY (user_id, email_id)
);
```

```bash
CREATE TABLE cluster_queue (
    file_id CHAR(36) PRIMARY KEY,
    user_id CHAR(36),
    file_type CHAR(5)
);
```

```bash
COMMIT;
```