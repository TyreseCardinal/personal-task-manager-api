import secrets

# Generate a random 32-byte hex key for the Flask SECRET_KEY
secret_key = secrets.token_hex(32)
# Generate a random 32-byte hex key for the JWT_SECRET_KEY
jwt_secret_key = secrets.token_hex(32)

print("SECRET_KEY:", secret_key)
print("JWT_SECRET_KEY:", jwt_secret_key)
