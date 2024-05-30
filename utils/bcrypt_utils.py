import bcrypt


# Function to hash a password
def hash_password(password):
    # Hash the password using bcrypt with a salt and default work factor
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


# Function to check if a password matches the hashed password
def check_password(password, hashed_password):
    # Check if the provided password matches the hashed password
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
